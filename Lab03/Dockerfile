# ARG przed FROM - wersja obrazu bazowego, ustawiana tylko na czas budowania
ARG BASE_VERSION=3.20
FROM alpine:${BASE_VERSION}

# ARG po FROM - dostępny tylko w trakcie budowania (docker build --build-arg AUTHOR=...)
ARG AUTHOR="student"

# ENV - zmienne widoczne w działającym kontenerze (nadpisywalne przez docker run -e)
ENV GREETING="Cześć" \
    AUTHOR=${AUTHOR}

# RUN - polecenie wykonywane podczas budowania (tworzy warstwę)
RUN mkdir -p /app

# ADD - dodanie plików z kontekstu budowania do obrazu
ADD banner.txt /app/banner.txt
ADD hello.sh /app/hello.sh

RUN chmod +x /app/hello.sh

# ENTRYPOINT - stały program uruchamiany z kontenerem
ENTRYPOINT ["/app/hello.sh"]

# CMD - domyślny argument dla ENTRYPOINT (łatwo go nadpisać)
CMD ["student"]