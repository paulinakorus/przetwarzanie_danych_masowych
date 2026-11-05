## Syntetyczny raport końcowy z Laboratorium 4

### 1. Wektoryzacja vs. czysty Python (NumPy)

* **Bezkonkurencyjna wydajność:** Przetwarzanie wektorowe w bibliotece NumPy zredukowało czas fitowania dla $10^6$ próbek do zaledwie **~61 ms** w Pythonie 3.13, co czyni je najszybszą metodą w całym eksperymencie.
* **Przyczyny techniczne:** NumPy omija narzut interpretera Pythona, operuje na ciągłych blokach pamięci RAM (bez wraperów `PyObject`) i wykorzystuje niskopoziomowe instrukcje wektorowe procesora (SIMD/AVX) w skompilowanym kodzie C. Wektoryzacja sprzętowa przewyższa dowolne próby zrównoleglania czystego kodu Pythona na poziomie interpretera.

---

### 2. Ewolucja wydajności CPython (3.10 $\rightarrow$ 3.12 $\rightarrow$ 3.13)

* **Skok wydajności sekwencyjnej:** Kod wykonywany w czystym Pythonie zanotował spadek czasu wykonania o **~31%** (z 146.4 ms w Pythonie 3.10 do 101.2 ms w Pythonie 3.13 dla $10^6$ próbek).
* **Faster CPython (PEP 659 / PEP 709):** Przełom wydajnościowy w Pythonie 3.12 i 3.13 wynika z wprowadzenia adaptacyjnego interpretera specjalizującego oraz inliningu wywołań funkcji, co drastycznie obniżyło narzut pętli `for` i funkcji `zip()`.
* **Nieśmiertelne Obiekty (PEP 683 - Immortal Objects):** W Pythonie 3.13 obiekty współdzielone posiadają stałe liczniki referencji. Zapobiega to unieważnianiu stron pamięci podczas wywołania `fork()`, dzięki czemu mechanizm *Copy-on-Write* w jądrze Linuksa działa efektywnie. Przełożyło się to na spadek czasu wersji wieloprocesowej dla $10^6$ próbek z 425 ms (Python 3.10) do **368 ms** (Python 3.13).
* **JIT i Tier 2 w Pythonie 3.13:** Dalsze prace nad zoptymalizowanym wywoływaniem kodu bajtowego (*uops bytecode optimizer*) pozwalają na wydajniejszą egzekucję operacji zmiennoprzecinkowych na pojedynczych rdzeniach.

---

### 3. Wielowątkowość (`LinearRegressionThreads`) a blokada GIL

* **Brak skalowalności CPU-bound:** Wielowątkowość w czystym Pythonie nie przyspiesza obliczeń obciążających procesor. Przebieg czasu w zależności od liczby wątków jest całkowicie płaski (~120–128 ms w 3.13 dla 1, 2, 4 i 8 wątków).
* **Zasada działania GIL:** Blokada *Global Interpreter Lock* wymusza sekwencyjne wykonywanie kodu bajtowego Pythona przez tylko jeden wątek naraz. Dodawanie kolejnych wątków nie przynosi zysku mocy obliczeniowej, a generuje jedynie narzut na przełączanie kontekstu i zarządzanie pulą `ThreadPoolExecutor`.
* **GIL w oficjalnych obrazach Docker:** Domyślny obraz `python:3.13-slim` jest kompilowany z aktywną blokadą GIL w celu zachowania kompatybilności wstecznej z C-API. Eksperymentalny tryb *free-threaded* (PEP 703) wymaga specjalnych kompilacji interpretera.

---

### 4. Wieloprocesowość (`LinearRegressionProcess`) – równoległość vs. narzut IPC

* **Realna równoległość:** Procesy omijają blokadę GIL poprzez tworzenie niezależnych przestrzeni adresowych i osobnych interpreterów Pythona. Pozwala to na rzeczywiste rozłożenie obliczeń na wiele rdzeni CPU (spadek czasu z 0.469 s przy 1 workerze do 0.361 s przy 8 workerach w Pythonie 3.13).
* **Wąskie gardło transmisji danych:** Głównym ograniczeniem wersji wieloprocesowej przy dużych zbiorach danych ($10^6$ próbek) pozostaje **narzut serializacji (`pickle`) oraz komunikacji międzyprocesowej (IPC)**. Przesyłanie wielomilionowych list przez potoki systemowe powoduje, że wieloprocesowość działa ~3.6x wolniej od kodu sekwencyjnego i ~6x wolniej od NumPy.

---

### 5. Wpływ środowiska uruchomieniowego i wersji zależności

* **Metoda tworzenia procesów (`fork` vs `spawn`):** Uruchomienie testów w kontenerze Docker (Linux) obniżyło czas wykonania `LinearRegressionProcess` z kilku sekund (w środowiskach używających `spawn`) do kilkuset milisekund dzięki szybkiej alokacji pamięci w metodzie `fork`.
* **Ewolucja NumPy (1.26.4 $\rightarrow$ 2.0.2 / 2.1.3):** Przejście na gałąź NumPy 2.x zoptymalizowało integrację z nowym C-API interpretera oraz usprawniło obsługę pętli SIMD, przynosząc stały przyrost prędkości operacji macierzowych o ~10% względem gałęzi 1.x.