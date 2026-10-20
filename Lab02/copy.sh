#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 3 ]; then
    echo "Użycie: $0 <użytkownik1@IP_źródła:/ścieżka> <użytkownik2@IP_celu:/ścieżka> <plik1[:nowa_nazwa1]> [plik2...]" >&2
    exit 1
fi

SRC_BASE="${1%/}"
DST_BASE="${2%/}"

shift 2

for item in "$@"; do
    if [[ "$item" == *:* ]]; then
        SRC_FILE="${item%%:*}"
        DST_FILE="${item#*:}"
    else
        SRC_FILE="$item"
        DST_FILE="$item"
    fi

    SRC_PATH="${SRC_BASE}/${SRC_FILE}"
    DST_PATH="${DST_BASE}/${DST_FILE}"

    echo "Kopiowanie: ${SRC_PATH} -> ${DST_PATH}"
    
    # Zamiana spacji na znaki ucieczki '\ ' dla zdalnych ścieżek w scp
    SRC_ESC="${SRC_PATH// /\\ }"
    DST_ESC="${DST_PATH// /\\ }"

    scp "$SRC_ESC" "$DST_ESC"
done