# Laboratorium 2
## Podstawy wykorzystania infrastruktury chmurowej - Unix, Shell

W trakcie zajęć laboratoryjnych będziemy pracować z różnymi narzędziami stosowanymi przy przetwarzaniu danych masowych. Wykorzystamy je, aby krok po kroku zbudować rozproszoną aplikację do zbierania i przetwarzania większych wolumenów danych, pochodzących z różnych źródeł. Będziemy również wdrażać tę aplikację na produkcyjnym środowisku. 

Zarówno na etapie rozwoju aplikacji, jak i jej późniejszego wdrożenia będziemy korzystać z usług chmurowych, a dokładniej z maszyn wirtualnych. Taki tryb pracy wymaga zapoznania się z podstawowymi mechanizmami w systemie Linux, który będzie używany na serwerach (maszynach wirtualnych). Jednymi z pierwszych aspektów, które poruszymy na tym laboratorium, jest obsługa powłoki (shell) Bash oraz praca z edytorami tekstowymi (tutaj: Vim).

## 1. Powłoka Bash

Najczęściej spotykaną powłoką w systemach z rodziny GNU/Linux jest **Bash** (ang. *Bourne-Again Shell*). Dostarcza ona wiele komend pozwalających na przeprowadzanie podstawowych operacji oraz interakcję z systemem (np. $\texttt{cd}, \texttt{pwd}, \texttt{echo}$). 

Komendy można łączyć w większe programy, zwane w Bashu skryptami. Skrypty mają najczęściej rozszerzenie $\texttt{.sh}$, ale jest to konwencja a nie wymaganie. Bash pozwoli uruchomić skrypt w pliku nie posiadającym żadnego rozszerzenia. Skrypty można uruchamiać na m.in. dwa sposoby: 
- `bash plik.sh`
- `./plik.sh`

W drugim przypadku wymagane jest dopisanie w pierwszej linii skryptu informacji jak uruchomić taki skrypt, tzw. *shebang*:

```
#!/usr/bin/env bash
```

lub

```
#!/bin/bash
```

Przy uruchamianiu skryptów za pomocą komendy `bash plik.sh` nie jest to wymagane, ale dopisywanie shebanga stanowi dobrą praktykę.

Więcej szczegółowych informacji na temat Basha można znaleźć w jego oficjalnej dokumentacji: [https://www.gnu.org/software/bash/manual/bash.html](https://www.gnu.org/software/bash/manual/bash.html)

## Zadanie 2.1
Napisz skrypt Bashowy, który **uruchomi w tle komendę** podaną jako argument do skryptu, tzn.
```
$ ./run-background.sh <command-to-run>
```

np.

```
$ ./run-background.sh "sleep 10"
$ ./run-background.sh "du -sh /home"
```

W implementacji wykorzystaj polecenie `&`.

Plik `run-background.sh`, w którym należy zaimplementować ten skrypt znajdziesz w repozytorium do tego laboratorium.

## Zadanie 2.2
Napisz skrypt Bashowy, który **wyszuka i zakończy działanie komendy** podanej jako argument do skryptu, tzn.
```
$ ./kill.sh <command-to-kill>
```

np.

```
$ ./kill.sh "sleep 10"
$ ./kill.sh "du -sh /home"
```

W implementacji wykorzystaj jedno lub kilka z następujących poleceń: `kill`, `killall`, `pidof`.

Plik `kill.sh`, w którym należy zaimplementować ten skrypt znajdziesz w repozytorium do tego laboratorium.

**Uwaga:** dobieraj procesy precyzyjnie, nie kończ cudzych procesów ani własnej powłoki. Sprawdź działanie na uruchomionym przez siebie procesie testowym.

## Zadanie 2.3
Napisz skrypt Bashowy, który **będzie filtrować dane pochodzące z losowego strumienia danych**. Wykorzystaj strumień `/dev/urandom` oraz komendy `sed` lub `tr`. Zaimplementuj filtrowanie w taki sposób, aby zwracać tylko znaki alfanumeryczne oraz wybrane 2-3 dodatkowe znaki.

```
$ ./filter.sh
```

## 2. Połączenia SSH
W celu połączenia się ze zdalnym serwerem (maszyną wirtualną) najczęściej wykorzystuje się protokół SSH (ang. *secure shell*). Podstawowa składnia stosowana do połączenia się z maszyną to:

```bash
ssh <użytkownik>@<adres-maszyny>
```

W przypadku adresu maszyny możemy podać zarówno adres IP maszyny, jak i adres domeny, który wskazuje na IP maszyny. 

Po wykonaniu komendy zostaniemy poproszeni o podanie hasła użytkownika na zdalnym serwerze. Bezpieczniejszą alternatywą jest wykorzystanie kluczy SSH, które możemy wskazać za pomocą argumentu `-i` do komendy `ssh`.

Wykorzystując protokół ssh możemy nie tylko połączyć się do zdalnej maszyny, ale również kopiować pliki, np. z lokalnej maszyny na zdalny serwer. Wykorzystujemy w tym celu komendę `scp` (ang. *secure copy*).

## Zadanie 2.4
Napisz skrypt Bashowy, który **skopiuje pliki podane jako argumenty skryptu z jednego serwera na drugi**. Powinna być możliwość opcjonalnej zmiany nazwy pliku. Składnia skryptu powinna być następująca:
```
$ ./copy.sh <użytkownik1@IP-maszyny-źródłowej:/ścieżka/do/plików/> <użytkownik2@IP-maszyny-docelowej:/ścieżka/do/plików> <plik-1>:<nowa-nazwa-pliku-1?> <plik-2>:<nowa-nazwa-pliku-2?> ... <plik-N>:<nowa-nazwa-pliku-N?>
```

Przykładowe wywołanie:
```
$ ./copy.sh bob@192.168.0.1:/home/bob alice@192.168.0.2:/tmp/ log.txt config.yaml:configuration.yaml
```

Powyższe polecenie skopiuje dwa pliki z maszyny o adresie `192.168.0.1` (logując się jako użytkownik `bob`) z katalogu `/home/bob` na maszynę o adresie `192.168.0.2` (logując się jako użytkownik `alice`) do katalogu `/tmp`. Pierwszy plik - `log.txt` - zostanie skopiowany bez zmian, natomiast w przypadku drugiego pliku - `config.yaml` - nazwa pliku powinna zostać zmieniona na `configuration.yaml`.

Pamiętaj, aby skrypt obsługiwał zmienną liczbę nazw plików, tzn. można skopiować 1 plik, ale również 50.

**Uwaga:** kopiowanie między dwoma zdalnymi hostami wymaga odpowiedniego dostępu SSH i obsługi przesyłu zdalnego przez zdalny. Określ sposób uwierzytelnienia i przetestuj skrypt na własnych hostach testowych.

## 3. Edytory tekstowe
W trakcie pracy na zdalnym serwerze będziemy często mieli potrzebę edycji zawartości plików tekstowych. Zamiast kopiować te pliki z serwera na lokalny komputer, edytować je lokalnie i następnie zmienione pliki z powrotem umieszczać na serwerze, możemy je edytować bezpośrednio na zdalnej maszynie. Nie będziemy mieć dostępu do aplikacji okienkowych, a jedynie będziemy w stanie wykorzystać edytory tekstowe działające w terminalu.

Popularnymi edytorami tekstu są: `nano`, `vi` oraz `vim`. O ile `nano` uchodzi za najprostszy edytor, o tyle `vim` oferuje największy komfort pracy. Edytor ten działa w kilku trybach:
- tryb poleceń (ang. *normal mode*) - włączony domyślnie po uruchomieniu vim'a; pozwala: (a) przechodzić w pozostałe tryby, (b) poruszać się po dokumencie (strzałki lub klawisze h, j, k, l), (c) usuwać, przenosić oraz kopiować tekst, 
- tryb wprowadzania (ang. *insert mode*) - w ten tryb wchodzimy za pomocą klawisza `i`, a wychodzimy za pomocą `Esc`; w tym trybie możemy normalnie wprowadzać/wpisywać tekst,
- tryb wizualny (ang. *visual mode*) - pozwala wybierać fragmenty tekstu i wykonywać na nich polecenia

Istnieją jeszcze dodatkowe tryby (*select*, *command-line*, *ex-mode*) jednak na razie je pominiemy. 

## Zadanie 2.5
Uruchom edytor `vim` na dowolnym pliku tekstowym, a następnie wykonaj poniższe polecenia:
- znajdź podane wyrażenie w tekście
- przejdź do podanej linii
- podmień pojedynczy znak
- podmień podane wyrażenie na inne
- zapisz zmiany
- wyjdź z vim'a (na dwa sposoby)

Zadanie to przećwicz wybierając sobie dowolne wyrażenia, znaki i linie w tekście, przy czym podczas oddawania zadania prowadzący poda własne przykłady.
