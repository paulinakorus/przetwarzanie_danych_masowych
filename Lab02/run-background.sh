#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Użycie: $0 \"<komenda-do-uruchomienia>\"" >&2
    exit 1
fi

# Uruchomienie komendy przekazanej w argumencie w tle za pomocą bash -c oraz &
bash -c "$1" &
PID=$!

echo "Uruchomiono w tle polecenie: '$1' (PID: $PID)"