#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Użycie: $0 \"<komenda-do-zakończenia>\"" >&2
    exit 1
fi

TARGET_CMD="$1"

# Wyszukiwanie procesów z wykluczeniem PID bieżącego skryptu ($$) oraz procesów potomnych
PIDS=$(pgrep -f "$TARGET_CMD" | grep -v -E "$$|$PPID" || true)

if [ -z "$PIDS" ]; then
    echo "Nie znaleziono pasujących procesów dla: '$TARGET_CMD'"
    exit 1
fi

# Zamiana znaków nowej linii na spacje dla czytelnego wyświetlania
PIDS_SINGLE_LINE=$(echo $PIDS | tr '\n' ' ')

echo "Zamykanie procesów o PID: $PIDS_SINGLE_LINE"

# Ciche zamykanie, aby zignorować ewentualnie uciekające podprocesy
kill $PIDS 2>/dev/null || true