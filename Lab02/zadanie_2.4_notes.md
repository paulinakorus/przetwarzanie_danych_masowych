### 1. Start usługi SSH i przygotowanie plików

#### `sudo service ssh start`

* **`sudo`** (*superuser do*) – uruchamia polecenie z uprawnieniami administratora systemowego (`root`). Zarządzanie demonami sieciowymi wymaga podwyższonych uprawnień.
* **`service`** – narzędzie systemowe używane do zarządzania usługami (skryptami startowymi SysVinit lub systemd).
* **`ssh`** – nazwa usługi serwera SSH (OpenSSH Daemon – `sshd`).
* **`start`** – polecenie uruchamiające usługę. Serwer SSH zaczyna nasłuchiwać na porcie 22 na przychodzące połączenia.

#### `echo "Plik logu" > log.txt`

* **`echo`** – wypisuje podany ciąg znaków na standardowe wyjście (`stdout`).
* **`>`** – operator przekierowania strumienia wyjściowego z trybem nadpisywania. Przechwytuje tekst i tworzy plik `log.txt` (lub czyści jego zawartość, jeśli już istnieje) i zapisuje do niego ciąg `"Plik logu"`.

#### `echo "Konfiguracja" > config.yaml`

* **`config.yaml`** – tworzy plik konfiguracyjny z zawartością `"Konfiguracja"`.

#### `chmod +x copy.sh`

* **`chmod`** (*change mode*) – komenda służąca do zmiany uprawnień/praw dostępu do plików i katalogów.
* **`+x`** (*executable*) – dodaje flagę wykonywalności dla pliku skryptu `copy.sh`. Bez tej opcji system odrzuci próbę bezpośredniego uruchomienia skryptu jako polecenia (`./copy.sh`) ze względu na brak uprawnień (`Permission denied`).

---

### 2. Konfiguracja bezhasłowego klucza SSH

#### `mkdir -p ~/.ssh`

* **`mkdir`** (*make directory*) – tworzy nowy katalog w systemie plików.
* **`-p`** (*parents*) – zapobiega zgłoszeniu błędu, jeśli katalog już istnieje, oraz w razie potrzeby tworzy brakujące katalogi nadrzędne.
* **`~/.ssh`** – tylda (`~`) oznacza katalog domowy użytkownika (np. `/home/jan`). Katalog `.ssh` jest domyślnym miejscem przechowywania kluczy i konfiguracji SSH (kropka na początku oznacza plik ukryty).

#### `[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519`

* **`[ -f ~/.ssh/id_ed25519 ]`** – test warunkowy sprawdzający, czy plik prywatnego klucza `id_ed25519` już istnieje w systemie.
* **`||`** – logiczny operator `OR`. Druga część komendy wykona się **tylko wtedy**, gdy pierwsza zwróci fałsz (czyli gdy klucz nie istnieje). Chroni to przed skasowaniem istniejących kluczy.
* **`ssh-keygen`** – dedykowane narzędzie pakietu OpenSSH do generowania par kluczy kryptograficznych (prywatnego i publicznego).
* **`-t ed25519`** – określa algorytm szyfrowania. **Ed25519** (krzywa eliptyczna) zapewnia najwyższy poziom bezpieczeństwa przy krótkim rozmiarze klucza i szybkiej weryfikacji.
* **`-N ""`** – ustawia nową frazę szyfrującą (*passphrase*) dla klucza prywatnego jako pustą (`""`). Dzięki temu klucz nie będzie wymagał wpisywania hasła przy każdym połączeniu.
* **`-f ~/.ssh/id_ed25519`** – jawnie wskazuje ścieżkę zapisu generowanego klucza prywatnego. Równolegle wygenerowany zostanie plik klucza publicznego z rozszerzeniem `.pub` (`id_ed25519.pub`).

#### `cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys`

* **`cat`** (*concatenate*) – odczytuje i przekazuje zawartość pliku klucza publicznego.
* **`>>`** – operator dopisywania do pliku (*append*). W przeciwieństwie do pojedynczego `>`, dodaje nową zawartość na końcu pliku bez usuwania dotychczasowych wpisów.
* **`authorized_keys`** – kluczowy plik konfiguracyjny serwera SSH. Zawiera listę kluczy publicznych, których posiadacze (osoby dysponujące pasującym kluczem prywatnym) są automatycznie wpuszczani do systemu bez pytania o hasło.

#### `chmod 700 ~/.ssh`

* **`700`** – zapis uprawnień w systemie ósemkowym:
* `7` (właściciel): pełne prawa – odczyt `r`, zapis `w`, wykonanie/wejście `x` ($4+2+1=7$).
* `0` (grupa) / `0` (inni): brak jakichkolwiek praw (`---`).


* Demon `sshd` rygorystycznie weryfikuje uprawnienia i **odrzuci połączenie**, jeśli katalog `.ssh` będzie miał prawa zapisu lub odczytu dla innych użytkowników.

#### `chmod 600 ~/.ssh/authorized_keys`

* **`600`** – uprawnienia ósemkowe dla pliku:
* `6` (właściciel): odczyt `r` i zapis `w` ($4+2=6$).
* `0` / `0`: brak dostępu dla reszty świata.


* Chroni plik autoryzacyjny przed modyfikacją lub odczytem przez nieuprawnione konta lokalne.

---

### 3. Test połączenia SSH

#### `ssh -o StrictHostKeyChecking=accept-new 127.0.0.1 "echo 'SSH działa poprawnie!'"`

* **`ssh`** – klient protokołu Secure Shell.
* **`-o StrictHostKeyChecking=accept-new`** – modyfikuje zachowanie sprawdzania tożsamości hosta. Zamiast wyświetlać interaktywne zapytanie `Are you sure you want to continue connecting (yes/no)?` przy pierwszym połączeniu, automatycznie dodaje klucz serwera do pliku `known_hosts` i kontynuuje.
* **`127.0.0.1`** – interfejs pętli zwrotnej (*loopback*), nawiązuje połączenie z lokalną maszyną.
* **`"echo 'SSH działa poprawnie!'"`** – komenda zdalna. Po nawiązaniu bezhasłowego połączenia serwer wykonuje to polecenie, zwraca wynik i natychmiast zamyka sesję SSH.

---

### 4. Wykonanie skryptu kopiującego

#### `./copy.sh "$USER@127.0.0.1:$(pwd)" "$USER@127.0.0.1:/tmp" log.txt config.yaml:configuration.yaml`

* **`./copy.sh`** – wywołanie lokalnego skryptu Basha.
* **`"$USER@127.0.0.1:$(pwd)"`** – **Argument 1 (źródło SSH)**:
* `$USER` – zmienna środowiskowa reprezentująca nazwę zalogowanego użytkownika.
* `$(pwd)` – podpowłoka zwracająca pełną ścieżkę do bieżącego katalogu roboczego.


* **`"$USER@127.0.0.1:/tmp"`** – **Argument 2 (cel SSH)**: określa konto, host oraz docelowy katalog `/tmp`.
* **`log.txt`** – **Argument 3**: plik źródłowy do przesłania.
* **`config.yaml:configuration.yaml`** – **Argument 4**: przekazanie pliku wraz ze wskazaniem zmienionej nazwy w miejscu docelowym (plik `config.yaml` ma zostać zapisany jako `configuration.yaml`).

---

### 5. Weryfikacja obecności skopiowanych plików

#### `ls -l /tmp/log.txt /tmp/configuration.yaml`

* **`ls`** (*list*) – wypisuje informacje o plikach i katalogach.
* **`-l`** (*long format*) – tryb szczegółowy, wyświetla uprawnienia, liczbę dowiązań, właściciela, grupę, rozmiar w bajtach, czas modyfikacji oraz nazwę pliku.
* **`/tmp/log.txt /tmp/configuration.yaml`** – jawnie podane ścieżki docelowe pozwalają sprawdzić, czy proces kopiowania i zmiana nazwy przebiegły pomyślnie.