# Laboratorium 6 – odpowiedzi i uruchomienie

## Uruchomienie (krok po kroku)

Pliki `docker-compose.yml` i `main.py` w jednym katalogu.

```bash
# 0. (opcjonalnie) sprawdź obraz – bitnami/spark ma już tylko :latest
docker manifest inspect bitnamilegacy/spark:3.5.5

# 1. master + 3 workery (+ init-data, które ustawia prawa do ./data)
docker compose up -d spark-master spark-worker
#    jeśli nie powstały 3 workery:
#    docker compose up -d --scale spark-worker=3 spark-master spark-worker
docker compose ps                     # powinno być 3x spark-worker
# Master UI: http://localhost:8080 -> "Alive Workers: 3"

# 2. w drugiej konsoli logi
docker compose logs -f

# 3. aplikacje
docker compose up spark-app                                  # 6.1 przykład + 6.2 + 6.3 (all)
# albo pojedynczo:
docker compose run --rm spark-app python3 /app/main.py numbers   # 6.2
docker compose run --rm spark-app python3 /app/main.py strings   # 6.3 zapis
docker compose run --rm spark-app python3 /app/main.py count     # 6.3 odczyt + liczenie znaków

# 4. zadanie 6.4 – Spark UI trzeba oglądać, gdy aplikacja żyje:
KEEP_ALIVE_SECONDS=300 docker compose run --rm --service-ports spark-app python3 /app/main.py count
# -> http://localhost:4040

# sprzątanie
docker compose down
docker compose run --rm init-data sh -c 'rm -rf /data/*'   # dane są własnością uid 1001
```

Parametry zad. 6.3 (przedział długości itd.) przez env, np.:
`docker compose run --rm -e STRING_MIN_LEN=10 -e STRING_MAX_LEN=100 spark-app python3 /app/main.py strings`

## 6.1 Architektura

* `spark-master` – standalone cluster manager (RPC 7077, UI 8080).
* `spark-worker` ×3 (`deploy.replicas`) – każdy 1 rdzeń i 2 GB; rejestrują się w masterze.
* `spark-app` – kontener z kodem pyspark działający jako **driver** (tryb client);
  zgłasza się do mastera, ten uruchamia executory na workerach. UI aplikacji: 4040.
* `init-data` + wolumen `./data` wspólny dla wszystkich – bez wspólnego dysku zapis
  z executorów trafiłby do lokalnych systemów plików workerów i driver by go nie zobaczył.

Wersja Sparka: w logu `spark-app` linia `SparkContext: Running Spark version X`
(oraz wypisuje ją `main.py`: `[info] Spark version`); także
`docker compose exec spark-master spark-submit --version`.

Obraz: z `bitnami/spark` zostało publicznie tylko `:latest` (wersjonowane tagi
przeniesiono do `bitnamilegacy/spark` / płatnej subskrypcji), a `latest` może mieć inną wersję
Sparka i py4j niż zakłada `PYTHONPATH`. Dlatego przypięto `bitnamilegacy/spark:3.5.5`
(py4j 0.10.9.7), zmienialne zmienną `SPARK_IMAGE`.
Uwaga: tutaj nie miałem dostępu do Docker Hub, więc istnienia tagu nie mogłem potwierdzić –
sprawdź komendą z kroku 0.

## 6.2 Ziarna generatorów

Ziarno bazowe losujemy **raz na driverze**, a w partycji używamy
`random.Random(f"{seed}:{index}")` (index z `mapPartitionsWithIndex`).
Dlaczego:

* Ten sam seed w każdej partycji (np. stała lub losowanie w każdym tasku z tym samym
  kodem) => wszystkie partycje dają **identyczny ciąg**: zamiast 10 mln niezależnych
  liczb mamy 10× te same 1 mln – psuje to statystykę (zaniżona wariancja estymatorów,
  duplikaty, błędne wyniki Monte Carlo).
* Ziarno z czasu losowane wewnątrz partycji bywa takie samo (taski startują w tej samej
  chwili) i, co gorsza, **przy ponownym obliczeniu partycji** (retry, utrata executora)
  dałoby inne dane – RDD przestaje być deterministyczną funkcją, więc wyniki zależą od awarii.
* Ziarno bazowe z drivera + indeks partycji: partycje są niezależne, a powtórne
  obliczenie partycji daje dokładnie te same dane. Złączenie jako napis (hashowany SHA-512)
  zamiast `seed + index` unika korelacji sąsiednich ziaren. `BASE_SEED=...` daje
  powtarzalny eksperyment.

Test (lokalnie, pyspark): 10 000 000 liczb, średnia 0,49996, 10 różnych pierwszych wartości na 10 partycji.

## 6.3 Stringi

`strings` generuje 1 000 000 stringów (alfanumeryczne, długość z [MIN, MAX]) i zapisuje
`df.write.text("/data/random_strings")` (10 plików part-*). `count` wczytuje je i liczy
liczbę stringów i znaków (`sum(length(value))`) oraz min/max/średnią długości.
Test lokalny: 1 000 000 stringów, 27 492 462 znaków (średnia 27,49 ≈ (5+50)/2).

## 6.4 DAG w Spark UI

Zadanie 3 (6.3) – gdy aplikacja działa (użyj `KEEP_ALIVE_SECONDS`):
`http://localhost:4040` → zakładka **Jobs** → kliknij job (np. „text at …” dla zapisu,
„first at …” dla liczenia) → **DAG Visualization**; ten sam graf per etap:
**Stages** → wybrany stage → DAG Visualization. Zapis: `parallelize → mapPartitionsWithIndex →
… → WriteFiles` w jednym stage (bez shuffle). Odczyt: Scan text → Project → HashAggregate
(partial) | Exchange | HashAggregate (final) – dwa stage’e rozdzielone shuffle’em.
Zakładka **SQL / DataFrame** pokazuje plan zapytania. Po zakończeniu aplikacji UI na 4040
znika (master UI 8080 → „Completed Applications” nie ma DAG-u bez event logów / history servera).
