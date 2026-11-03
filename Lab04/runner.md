Komendy uruchamiasz w terminalu PyCharma (zakładka Terminal), w katalogu `Lab04`.

**1. Środowisko i testy**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install numpy matplotlib threadpoolctl pytest
pip install -e .
pytest -s tests/
```
`threadpoolctl` jest opcjonalny, ale dzięki niemu w JSON-ie zapiszą się wątki BLAS. Komenda `activate` jest dla Windows. W Git Bashu użyj `source .venv/Scripts/activate`.

**2. Zadania 4.1 i 4.3 ręcznie**
```bash
python scripts/generate_data.py --num-samples 10000 --out-dir data/datasets
python scripts/generate_data.py --num-samples 100000 --out-dir data/datasets
python scripts/generate_data.py --num-samples 1000000 --out-dir data/datasets
python scripts/run_experiments.py --datasets-dir data/datasets
```
Wyniki trafią do `data/time_measurements.json`, `data/comparison.png` i `data/scaling.png`.

**3. Zadanie 4.4 w Dockerze**
Uruchom Docker Desktop. Potem w Git Bashu lub WSL (nie w cmd ani PowerShellu):
```bash
bash run_all.sh
```
Wyniki dla każdej wersji Pythona będą w `data/py3.10/`, `data/py3.12/` i `data/py3.13/`.

Jeśli w Git Bashu `docker run` zgłosi problem ze ścieżką `$PWD`, uruchom skrypt z `MSYS_NO_PATHCONV=1`:
```bash
MSYS_NO_PATHCONV=1 bash run_all.sh
```

Na Windowsie procesy używają `spawn`, więc pierwszy pomiar `LinearRegressionProcess` może być wolniejszy. Dlatego skrypt robi rozgrzewkę i dopiero potem mierzy.