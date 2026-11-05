# Comparison

Wykres przedstawia czasy wykonania w **skali podwójnie logarytmicznej** (log-log). Dzięki tej skali różnice wysokości między liniami nie oznaczają drobnych ułamków sekund, lecz **całe rzędy wielkości (krotności 10x)**.

Oto szczegółowa analiza przyczyn położenia poszczególnych linii na wykresie – od najwolniejszej (najwyżej) do najszybszej (najniżej):

---

### 1. Linia najwyższa (najwolniejsza): `LinearRegressionProcess` (Pomarańczowa)



Wersja wieloprocesowa wykonuje się najdłużej ($1{,}8\text{ s} \text{ do } 6{,}4\text{ s}$). Wynika to bezpośrednio z architektury pamięciowej systemów operacyjnych i Pythona:

* **Narzut serializacji (`pickle`)**: Procesy nie dzielą pamięci operacyjnej RAM. Aby przekazać dane ze zbioru $X$ i $y$ do 4 osobnych procesów roboczych, główny proces musi zamienić miliony obiektów Pythona na ciąg bajtów (`pickle.dumps`). Proces potomny musi ten ciąg odbrać i zdeserializować back na listy (`pickle.loads`).
* **Komunikacja międzyprocesowa (IPC)**: Przesyłanie dużych ilości zserializowanych danych przez łącza IPC (pipes/sockets) tworzy ogromne wąskie gardło I/O i pamięci.
* **Koszt tworzenia procesów**: Utworzenie nowego procesu systemowego wymaga alokacji osobnej przestrzeni adresowej i załadowania nowego interpretera Pythona.
* **Wynik**: Czas poświęcony na kopiowanie i przesyłanie danych wielokrotnie przewyższa czas samych obliczeń matematycznych.

---

### 2. Linia druga od góry (wolna): `LinearRegressionSequential` (Zielona)



Kod sekwencyjny w czystym Pythonie plasuje się wysoko ($0{,}009\text{ s} \text{ do } 0{,}41\text{ s}$) z powodu narzutu samych mechanizmów interpretera CPython:

* **Pętla w czystym Pythonie**: Każdy krok pętli `for xi, yi in zip(xs, ys)` wymaga interpretacji kodu bajtowego (bytecode).
* **Dynamiczne typowanie i "boxing" (PyObject)**: Liczby zmiennoprzecinkowe w Pythonie nie są surowymi bajtami w pamięci, lecz pełnymi obiektami struktury C (`PyObject`). Przy każdym dodawaniu i mnożeniu interpreter musi:
1. Odczytać typ obiektu.
2. Wyciągnąć wartość liczbową.
3. Wykonać operację.
4. Utworzyć nowy obiekt `PyObject` dla wyniku i obsłużyć licznik referencji (garbage collection).


* **Brak równoległości**: Całość wykonuje się po kolei na jednym rdzeniu CPU.

---

### 3. Linia trzecia od góry: `LinearRegressionThreads` (Czerwona)



Wielowątkowość w czystym Pythonie działa minimalnie szybciej niż kod sekwencyjny ($0{,}007\text{ s} \text{ do } 0{,}34\text{ s}$), ale biegnie niemal równolegle do niego. Wynika to z działania blokady GIL:

* **Global Interpreter Lock (GIL)**: W standardowym Pythonie (CPython) GIL zezwala na wykonywanie kodu bajtowego Pythona **tylko jednemu wątkowi naraz**.
* Mimo podzielenia danych na 4 wątki, pętla `for` w funkcji `_partial_sums` nie wykonuje się fizycznie równolegle na 4 rdzeniach CPU. Wątki wykonują się naprzemiennie (time-slicing).
* Niewielki zysk czasowy wynika głównie z podziału danych na mniejsze paczki i budowy mniejszych struktur cząstkowych, ale narzut na zarządzanie wątkami i przełączanie kontekstu zapobiega uzyskaniu 4-krotnego przyspieszenia.

---

### 4. Linia najniższa (najszybsza): `LinearRegressionNumpy` (Niebieska)



Wersja NumPy jest bezkonkurencyjnie najszybsza ($0{,}0013\text{ s} \text{ do } 0{,}14\text{ s}$) — działa niemal **3x szybciej od wątków i ponad 45x szybciej od procesów**:

* **Kompilowany kod C / Fortran**: NumPy omija interpreter Pythona. Operacje sumowania (`.sum()`) i iloczynu skalarnego (`np.dot()`) wykonują się całkowicie w niskopoziomowym kodzie C.
* **Ciągłość pamięci (Contiguous Memory)**: Tablica NumPy reprezentuje ciągły blok bajtów w RAM-ie (surowe 64-bitowe floaty bez wrapperów `PyObject`). Pozwala to na maksymalne wykorzystanie pamięci podręcznej procesora (Cache L1/L2/L3) i prefetchingu.
* **Wektoryzacja SIMD**: Procesor wykorzystuje instrukcje wektorowe (np. AVX/AVX2), wykonując mnożenie i dodawanie na wielu liczbach naraz w pojedynczym cyklu zegara procesora.
* Mimo ograniczenia biblioteki BLAS do 1 wątku (`OPENBLAS_NUM_THREADS=1`), optymalizacja sprzętowa w C całkowicie deklasuje wielowątkowy kod pisany w czystym Pythonie.

# Scaling
Wykres przedstawia czasy wykonania w **skali podwójnie logarytmicznej** (log-log). Dzięki tej skali różnice wysokości między liniami nie oznaczają drobnych ułamków sekund, lecz **całe rzędy wielkości (krotności 10x)**.

Oto szczegółowa analiza przyczyn położenia poszczególnych linii na wykresie – od najwolniejszej (najwyżej) do najszybszej (najniżej):

---

### 1. Linia najwyższa (najwolniejsza): `LinearRegressionProcess` (Pomarańczowa)



Wersja wieloprocesowa wykonuje się najdłużej ($1{,}8\text{ s} \text{ do } 6{,}4\text{ s}$). Wynika to bezpośrednio z architektury pamięciowej systemów operacyjnych i Pythona:

* **Narzut serializacji (`pickle`)**: Procesy nie dzielą pamięci operacyjnej RAM. Aby przekazać dane ze zbioru $X$ i $y$ do 4 osobnych procesów roboczych, główny proces musi zamienić miliony obiektów Pythona na ciąg bajtów (`pickle.dumps`). Proces potomny musi ten ciąg odbrać i zdeserializować back na listy (`pickle.loads`).
* **Komunikacja międzyprocesowa (IPC)**: Przesyłanie dużych ilości zserializowanych danych przez łącza IPC (pipes/sockets) tworzy ogromne wąskie gardło I/O i pamięci.
* **Koszt tworzenia procesów**: Utworzenie nowego procesu systemowego wymaga alokacji osobnej przestrzeni adresowej i załadowania nowego interpretera Pythona.
* **Wynik**: Czas poświęcony na kopiowanie i przesyłanie danych wielokrotnie przewyższa czas samych obliczeń matematycznych.

---

### 2. Linia druga od góry (wolna): `LinearRegressionSequential` (Zielona)



Kod sekwencyjny w czystym Pythonie plasuje się wysoko ($0{,}009\text{ s} \text{ do } 0{,}41\text{ s}$) z powodu narzutu samych mechanizmów interpretera CPython:

* **Pętla w czystym Pythonie**: Każdy krok pętli `for xi, yi in zip(xs, ys)` wymaga interpretacji kodu bajtowego (bytecode).
* **Dynamiczne typowanie i "boxing" (PyObject)**: Liczby zmiennoprzecinkowe w Pythonie nie są surowymi bajtami w pamięci, lecz pełnymi obiektami struktury C (`PyObject`). Przy każdym dodawaniu i mnożeniu interpreter musi:
1. Odczytać typ obiektu.
2. Wyciągnąć wartość liczbową.
3. Wykonać operację.
4. Utworzyć nowy obiekt `PyObject` dla wyniku i obsłużyć licznik referencji (garbage collection).


* **Brak równoległości**: Całość wykonuje się po kolei na jednym rdzeniu CPU.

---

### 3. Linia trzecia od góry: `LinearRegressionThreads` (Czerwona)



Wielowątkowość w czystym Pythonie działa minimalnie szybciej niż kod sekwencyjny ($0{,}007\text{ s} \text{ do } 0{,}34\text{ s}$), ale biegnie niemal równolegle do niego. Wynika to z działania blokady GIL:

* **Global Interpreter Lock (GIL)**: W standardowym Pythonie (CPython) GIL zezwala na wykonywanie kodu bajtowego Pythona **tylko jednemu wątkowi naraz**.
* Mimo podzielenia danych na 4 wątki, pętla `for` w funkcji `_partial_sums` nie wykonuje się fizycznie równolegle na 4 rdzeniach CPU. Wątki wykonują się naprzemiennie (time-slicing).
* Niewielki zysk czasowy wynika głównie z podziału danych na mniejsze paczki i budowy mniejszych struktur cząstkowych, ale narzut na zarządzanie wątkami i przełączanie kontekstu zapobiega uzyskaniu 4-krotnego przyspieszenia.

---

### 4. Linia najniższa (najszybsza): `LinearRegressionNumpy` (Niebieska)



Wersja NumPy jest bezkonkurencyjnie najszybsza ($0{,}0013\text{ s} \text{ do } 0{,}14\text{ s}$) — działa niemal **3x szybciej od wątków i ponad 45x szybciej od procesów**:

* **Kompilowany kod C / Fortran**: NumPy omija interpreter Pythona. Operacje sumowania (`.sum()`) i iloczynu skalarnego (`np.dot()`) wykonują się całkowicie w niskopoziomowym kodzie C.
* **Ciągłość pamięci (Contiguous Memory)**: Tablica NumPy reprezentuje ciągły blok bajtów w RAM-ie (surowe 64-bitowe floaty bez wrapperów `PyObject`). Pozwala to na maksymalne wykorzystanie pamięci podręcznej procesora (Cache L1/L2/L3) i prefetchingu.
* **Wektoryzacja SIMD**: Procesor wykorzystuje instrukcje wektorowe (np. AVX/AVX2), wykonując mnożenie i dodawanie na wielu liczbach naraz w pojedynczym cyklu zegara procesora.
* Mimo ograniczenia biblioteki BLAS do 1 wątku (`OPENBLAS_NUM_THREADS=1`), optymalizacja sprzętowa w C całkowicie deklasuje wielowątkowy kod pisany w czystym Pythonie.