1) Jaka jest różnica między `ENTRYPOINT` a `CMD`?

**Odpowiedź:**
`ENTRYPOINT` określa program, który jest uruchamiany zawsze po starcie kontenera – kontener zachowuje się jak „plik wykonywalny”. `CMD` określa domyślne polecenie lub (gdy jest `ENTRYPOINT`) domyślne argumenty dla `ENTRYPOINT`; jest to wartość łatwa do podmiany przy `docker run`. Najczęściej używa się ich razem: `ENTRYPOINT ["python", "app.py"]` + `CMD ["student"]` daje `python app.py student`, a `docker run obraz ktos` uruchomi `python app.py ktos`. Jeśli nie ma `ENTRYPOINT`, `CMD` jest całym uruchamianym poleceniem. Zalecana jest forma exec (`["program", "arg"]`), a nie shellowa, bo wtedy proces jest PID 1 i poprawnie odbiera sygnały (np. `SIGTERM`).


2) Jak każdą z powyższych opcji nadpisać podczas uruchamiania kontenera?

**Odpowiedź:**
- `CMD` – wystarczy podać polecenie/argumenty po nazwie obrazu: `docker run --rm hello:1.0 Jan` (w Compose: `command:`).
- `ENTRYPOINT` – flagą `--entrypoint`: `docker run --rm --entrypoint /bin/sh hello:1.0 -c "echo test"` (w Compose: `entrypoint:`). Argumenty podane po nazwie obrazu trafiają wtedy jako nowy `CMD` do nowego entrypointu.


3) Jaka jest różnica między `ADD` a `COPY`?

**Odpowiedź:**
`COPY` robi tylko jedno: kopiuje pliki i katalogi z kontekstu budowania do obrazu. `ADD` robi to samo, ale ma dodatkowe funkcje: automatycznie rozpakowuje lokalne archiwa (np. `.tar`, `.tar.gz`) do katalogu docelowego oraz potrafi pobierać pliki z adresów URL (i repozytoriów git). Te „magiczne” zachowania bywają niejednoznaczne, dlatego dobrą praktyką jest używanie `COPY`, a `ADD` tylko wtedy, gdy faktycznie potrzebne są jego dodatkowe możliwości.


4) Czy tylko jedno słowo kluczowe `FROM` może występować w pojedynczym pliku Dockerfile?

**Odpowiedź:**
Nie, w jednym pliku Dockerfile może być wiele instrukcji `FROM`. Każda z nich rozpoczyna nowy etap (stage) – tzw. budowanie wieloetapowe (*multi-stage build*). Pozwala to np. skompilować aplikację w ciężkim obrazie z kompilatorem, a do końcowego, małego obrazu skopiować tylko wynik (`COPY --from=builder ...`). Finalnym obrazem jest ostatni etap (lub wskazany przez `--target`). Dodatkowo przed pierwszym `FROM` mogą stać instrukcje `ARG`.