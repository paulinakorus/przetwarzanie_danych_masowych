#!/usr/bin/env bash
set -euo pipefail

SIZES=(10000 100000 1000000)
DATASETS_DIR=data/datasets

declare -A NUMPY_VERSION=(
    ["3.10"]="1.26.4"
    ["3.12"]="2.0.2"
    ["3.13"]="2.1.3"
)

for n in "${SIZES[@]}"; do
    docker run --rm -v "$PWD":/app -w /app python:3.12-slim \
        python scripts/generate_data.py --num-samples "$n" --out-dir "$DATASETS_DIR"
done

for py in 3.10 3.12 3.13; do
    np_ver="${NUMPY_VERSION[$py]}"
    docker run --rm -v "$PWD":/app -w /app -e PYTHONPATH=/app \
        -e OPENBLAS_NUM_THREADS=1 python:"$py"-slim \
        bash -c "pip install -q numpy==$np_ver matplotlib threadpoolctl && \
                 python scripts/run_experiments.py \
                     --datasets-dir $DATASETS_DIR --out-dir data/py$py"
done