# Laboratorium 6

## Wykorzystanie Spark w trybie wsadowym

### Linki

* [Apache Spark internals](https://books.japila.pl/apache-spark-internals/overview/)
* [Mastering Spark SQL](https://jaceklaskowski.gitbooks.io/mastering-spark-sql/content/)
* [Spark Docs](https://spark.apache.org/docs/latest/quick-start.html)

## Zadanie 6.1 

Przeanalizuj załączonego w repozytorium docker-compose.yml. Jak wygląda architektura przygotowanego systemu? 

Uruchom środowisko:
- najpierw uruchom mastera i workery: `docker compose up -d spark-master spark-worker`
- w osobnej konsoli wyświetl logi: `docker compose logs -f`
- następnie uruchom przykładową aplikację: `docker compose up spark-app`

Znajdź w logach informację o wersji Sparka. Przed uruchomieniem sprawdź dostępność i zgodność obrazu `bitnami/spark:latest` w wybranym rejestrze. Na potrzeby powtarzalności eksperymentów warto ustalić konkretny, dostępny tag obrazu. Jeśli pracujesz na zwykłym Docker Compose, sprawdź rzeczywistą liczbę workerów (`docker compose ps`); w razie potrzeby użyj `docker compose up -d --scale spark-worker=3 spark-master spark-worker`.

## Zadanie 6.2

Stwórz aplikację Spark, która wygeneruje 10 000 000 losowych liczb double w 10 partycjach. Stwórz na początku listę 10 liczb, z wykorzystaniem sparka dokonaj rozproszenia, zmapuj każdą partycję na odpowiednią liczbę losowych doubli. W jaki sposób zainicjować generator liczb losowych tak aby liczby były losowe oraz mieć pewność że nie trafimy na sytuację gdy dwie partycje mają taki sam seed (sygnatura funkcji mapowania pozwala poznać indeks partycji; użyj go do wyprowadzenia niezależnych ziaren generatorów), dlaczego należy tak robić?

## Zadanie 6.3

Stwórz aplikację spark, która wygeneruje 1 000 000 losowych stringów o losowej długości z zadanego (konfigurowalnego przedziału), następnie zapisz je na dysku. Stwórz kolejną aplikację która wczyta zapisane dane oraz policzy liczbe znaków.

## Zadanie 6.4

Zapoznaj się ze Spark-UI. Znajdź stronę na której widać DAG dla zadania 3.
