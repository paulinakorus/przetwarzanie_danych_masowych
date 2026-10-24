#!/usr/bin/env bash
# Użycie: ./publish.sh </path/to/Dockerfile>
#
# Zmienne środowiskowe:
#   DOCKERHUB_USER  (wymagana)  login na Docker Hub
#   IMAGE_NAME      (opcjonalna, domyślnie: lab3-hello)
#   IMAGE_TAG       (opcjonalna, domyślnie: latest)
#
# Przykład:
#   docker login
#   DOCKERHUB_USER=mojlogin ./publish.sh ./Dockerfile

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Użycie: $0 </path/to/Dockerfile>" >&2
  exit 1
fi

DOCKERFILE="$1"

if [[ ! -f "$DOCKERFILE" ]]; then
  echo "Błąd: plik '$DOCKERFILE' nie istnieje." >&2
  exit 1
fi

if [[ -z "${DOCKERHUB_USER:-}" ]]; then
  echo "Błąd: ustaw zmienną DOCKERHUB_USER (login na Docker Hub)." >&2
  exit 1
fi

IMAGE_NAME="${IMAGE_NAME:-lab3-hello}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE="${DOCKERHUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
CONTEXT="$(dirname "$DOCKERFILE")"

echo ">>> Budowanie obrazu ${IMAGE} (Dockerfile: ${DOCKERFILE})"
docker build -f "$DOCKERFILE" -t "$IMAGE" "$CONTEXT"

echo ">>> Wysyłanie obrazu ${IMAGE} na Docker Hub"
docker push "$IMAGE"

echo ">>> Gotowe: https://hub.docker.com/r/${DOCKERHUB_USER}/${IMAGE_NAME}"