1) Jaka jest różnica między `ENTRYPOINT` a `CMD`?

**Odpowiedź:**
`ENTRYPOINT` określa program, który jest uruchamiany zawsze po starcie kontenera, dzięki czemu kontener zachowuje się jak plik wykonywalny. `CMD` określa domyślne polecenie lub (gdy jest `ENTRYPOINT`) domyślne argumenty dla `ENTRYPOINT`; jest to wartość łatwa do podmiany przy `docker run`. Najczęściej używa się ich razem: `ENTRYPOINT ["python", "app.py"]` + `CMD ["student"]` daje `python app.py student`, a `docker run obraz ktos` uruchomi `python app.py ktos`. Jeśli nie ma `ENTRYPOINT`, `CMD` jest całym uruchamianym poleceniem. Zalecana jest forma exec (`["program", "arg"]`), a nie shellowa (`ENTRYPOINT program arg`). W formie exec proces jest PID 1 i poprawnie odbiera sygnały (np. `SIGTERM`), a w formie shellowej program jest uruchamiany przez `/bin/sh -c`, a `CMD` ani argumenty z `docker run` nie są do niego przekazywane.


2) Jak każdą z powyższych opcji nadpisać podczas uruchamiania kontenera?

**Odpowiedź:**
- `CMD` - wystarczy podać polecenie lub argumenty po nazwie obrazu: `docker run --rm hello:1.0 Jan` (w Compose: `command:`).
- `ENTRYPOINT` - flagą `--entrypoint`: `docker run --rm --entrypoint /bin/sh hello:1.0 -c "echo test"` (w Compose: `entrypoint:`). Argumenty podane po nazwie obrazu trafiają wtedy jako nowy `CMD` do nowego entrypointu. Nadpisanie `ENTRYPOINT` czyści także domyślny `CMD` z obrazu, więc potrzebne argumenty trzeba podać ręcznie.
- Oba naraz: `docker run --rm --entrypoint echo hello:1.0 "inny tekst"` uruchomi `echo "inny tekst"`, bez `/app/hello.sh` i bez domyślnego `student`.


3) Jaka jest różnica między `ADD` a `COPY`?

**Odpowiedź:**
`COPY` robi tylko jedno: kopiuje pliki i katalogi z kontekstu budowania do obrazu. `ADD` robi to samo, ale ma dodatkowe funkcje: automatycznie rozpakowuje lokalne archiwa (np. `.tar`, `.tar.gz`) do katalogu docelowego oraz potrafi pobierać pliki z adresów URL (i repozytoriów git). Pobrany z URL plik nie jest przy tym rozpakowywany. Te dodatkowe zachowania bywają niejednoznaczne, dlatego dobrą praktyką jest używanie `COPY`, a `ADD` tylko wtedy, gdy faktycznie potrzebne są jego dodatkowe możliwości.


4) Czy tylko jedno słowo kluczowe `FROM` może występować w pojedynczym pliku Dockerfile?

**Odpowiedź:**
Nie, w jednym pliku Dockerfile może być wiele instrukcji `FROM`. Każda z nich rozpoczyna nowy etap (stage), czyli tzw. budowanie wieloetapowe (*multi-stage build*). Pozwala to np. skompilować aplikację w ciężkim obrazie z kompilatorem, a do końcowego, małego obrazu skopiować tylko wynik (`COPY --from=builder ...`). Finalnym obrazem jest ostatni etap (lub wskazany przez `--target`). Dodatkowo przed pierwszym `FROM` mogą stać instrukcje `ARG`.