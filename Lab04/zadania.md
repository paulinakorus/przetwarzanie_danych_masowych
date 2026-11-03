# Laboratorium 4
## Ewaluacja metod zrównoleglania zadań - Python, wątki i procesy

W trakcie trzeciego wykładu wspominaliśmy o tym, że z perspektywy programisty mamy kilka sposobów zrównoleglania obliczeń. Głównie są to **wątki** i **procesy**. Staramy się używać wątków m.in. ze względu na krótszy czas tworzenia oraz współdzieloną pamięć, której nie mamy bezpośrednio dostępnej w procesach. Tworzenie procesu jest również bardziej czasochłonne, ponieważ wymaga ono większej interakcji z jądrem systemowym oraz utworzenia kopii przestrzeni pamięci.

Przez wiele lat używanie wątków w Pythonie nie było polecaną metodą ze względu na tzw. **Global Interpreter Lock** (GIL). Implementacja Pythona wymagała, aby w danym momencie tylko jeden wątek na raz miał dostęp do GILa. Takie założenie powoduje, że zrównoleglanie za pomocą wątków było wolniejsze niż za pomocą procesów.

W trakcie obecnego laboratorium będziemy porównywać czasy działania różnych metod zrównoleglania i przyspieszania obliczeń w języku Python. Zaimplementujemy kilka wersji modelu regresji liniowej.

## Zadanie 4.1.
W pliku `scripts/generate_data.py` zaimplementuj funkcję `generate_data()`, która wygeneruje zadaną liczbę `num_samples` próbek danych. Każda próbka $(x_i, y_i)$ powinna być opisana przez dwie liczby rzeczywiste, które są ze sobą związane poprzez wybraną funkcję liniową, np. $y_i = 2x_i + 5$ (lub inną klasę funkcji, którą dopasować za pomocą regresji liniowej).

Następnie zaimplementuj funkcję `main()` w taki sposób, aby wywołanie skryptu:
```bash
$ python3 scripts/generate_data.py --num-samples <num-samples> --out-dir </path/to/datasets/>
```
wygenerowało zbiór danych składający się z `<num-samples>` instancji i zapisało w katalogu `</path/to/datasets/>` plik o nazwie `<num-samples>.pkl` (bądź innym rozszerzeniu).

## Zadanie 4.2.
Zaimplementuj model regresji liniowej na 4 sposoby:
- `lr/lr_seq.py` - implementacja wykorzystująca sekwencyjne obliczenia (bez używania zewnętrznych bibliotek (typu NumPy, SciPy); kod ten będzie używany jako metoda referencyjna,
- `lr/lr_np.py` - implementacja obliczająca współczynniki regresji liniowej za pomocą biblioteki NumPy,
- `lr/lr_thread.py` - implementacja dzieląca dane na mniejsze paczki (ang. *batch*), obliczająca równolegle (za pomocą wątków) pośrednie wartości i agregująca je do końcowego wyliczenia współczynników regresji,
- `lr/lr_proc.py` - implementacja jak w przypadku `lr/lr_thread.py`, ale wykorzystująca procesy zamiast wątków.

Chcąc przetestować poprawność implementacji możesz użyć przygotowanych testów:
```bash
# Wewnątrz wirtualnego środowiska
pip install -e .
pip install pytest
pytest -s tests/
```

## Zadanie 4.3.
Uzupełnij implementację skryptu `scripts/run_experiments.py`:
- wczytaj zbiory danych z katalogu podanego w wywołaniu skryptu,
- uruchom każdą z zaimplementowanych wersji regresji liniowej na każdym ze zbiorów danych, pamiętając o odpowiednim sposobie pomiaru czasu oraz kilkukrotnym powtórzeniu pomiarów
- zbierz wyniki i zapisz je w pliku JSON (`data/time_measurements.json`)
- wygeneruj wykres pozwalający porównać szybkość działania każdej metody (`data/comparison.png`)
- wygeneruj wykres zależności liczby wątków / procesów a czasu działania skryptu (`data/scaling.png`)

## Zadanie 4.4.
Napisz skrypt Bashowy (`run_all.sh`), który:
- wygeneruje kilka zbiorów danych o różnej liczbie instancji
- uruchomi eksperymenty
- użyj kontenerów Dockerowych, aby uruchomić eksperymenty pod różnymi wersjami Pythona, np. 3.10, 3.11, 3.12, 3.13 (zbadaj minimum 3 różne wersje)

Uwaga: w starszych wersjach Pythona będziesz musiał użyć innych wersji zależności (np. Numpy) - dobierz wersje zależności do każdej porównywanej wersji Pythona; przy porównywaniu wyników uwzględnij także wpływ wersji bibliotek i liczby wątków BLAS
