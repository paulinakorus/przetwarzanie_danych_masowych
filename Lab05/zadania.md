# Laboratorium 5

## Wykorzystanie przetwarzania opartego o broker wiadomości

Podczas ostatniego laboratorium przećwiczyliśmy metody zrównoleglania oparte o wątki i procesy. Pozwalają one uruchamiać kod równolegle w obrębie jednego systemu.

Jedną z najpopularniejszych metod zrównoleglania pozwalającą na użycie wielu maszyn jest przetwarzanie oparte o broker wiadomości (ang. _message passing_). Pozwala ono na wykonywanie zadań w trybie asynchronicznym, dzięki czemu jest idealnym rozwiązaniem do implementacji architektury opartej o mikroserwisy.

**Podstawowe pojęcia**
- wiadomość - tekstowa porcja informacji przekazywana pomiędzy elementami systemu, najczęściej w formacie JSON
- kolejka - lista wiadomości
- producent - skrypt który generuje wiadomości i publikuje je do kolejki
- konsument - skrypt który przetwarza wiadomości, ściągając je z kolejki
- broker wiadomości - system zarządzający kolejkami i przesyłem wiadomości. Najpopularniejsze to [RabbitMQ](https://www.rabbitmq.com/) lub [Kafka](https://kafka.apache.org/), ale istnieje wiele możliwych rozwiązań

**Zalety systemów kolejkowych**
- łatwość implementacji i mniejsza szansa na popełnienienie błędów niz w podejściu ze współdzieleniem pamięci
- działanie w trybie asynchronicznym
- możliwość wykorzystania wielu maszyn lub klastrów
- możliwość złączenia skryptów w różnych językach
- enkapsulacja i izolacja zadań i zasobów
- mnogość konfiguracji routingu (np. implementacja wzorca EventBus)


**Wady systemów kolejkowych**
- narzut czasowy i zasobowy na komunikację 

## Message Passing w Pythonie

Najpopularniejszy broker, RabbitMQ, używa do komunikacji protokołu AMQP (ang. Asynchronous Message Queuing Protocol), który jest implementowany przez mnogość bibliotek - np. [pika](https://pypi.org/project/pika/)

Polecaną biblioteką do obsługi komunikacji opartej o wiadomości jest [Celery](https://pypi.org/project/celery/). Jest warstwą abstrakcji nad brokerami, umożliwiając w łatwy sposób definiowanie zadań, uruchamianie workerów i kontrolę nad przepływem wiadomości w systemie. Posiada także możliwość wpięcia różnych od RabbitMQ brokerów - np. Redisa, baz SQL, Memcache czy Cassandry. Każdy z nich posiada swoje wady i zalety, jednak ich dokładne zróżnicowanie jest poza zakresem niniejszego laboratorium.

## Zadanie 5.1

Przygotuj środowisko do użycia biblioteki Celery z brokerem wiadomości RabbitMQ. Zbuduj odpowiednie obrazy Dockera i zainstaluj potrzebne paczki.

Stwórz task Celery który będzie zwracał losowy numer z przedziału [0; 200]

Uruchom skrypt który wygeneruje asynchronicznie 100 losowych numerów używając w/w taska 

## Zadanie 5.2

Stwórz task Celery, który będzie:

a) przyjmował jako parametr numer `n` 

b) pobierał losowy artykuł z polskiej Wikipedii - dostęp pod linkiem [https://pl.wikipedia.org/wiki/Special:Random](https://pl.wikipedia.org/wiki/Special:Random). Użyj odpowiednich bibliotek do scrapowania, by uzyskać samą treść artykułu - np. [Requests](https://pypi.org/project/requests/) i [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)

c) zwracał `n-te` słowo z pobranego artykułu (ustal, czy numerowanie zaczyna się od 0 czy 1, oraz obsłuż przypadek zbyt krótkiego artykułu i błędów HTTP)

## Zadanie 5.3

Stwórz task Celery, który będzie:

a) przyjmował jako parametr słowo

b) zapisywał je do pliku tekstowego w formie "poematu" (5 słów per linia)

Pamiętaj o bezpiecznej synchronizacji zapisu. **Uwaga:** zwykły `threading.Lock` nie synchronizuje osobnych procesów ani kontenerów. Zastosuj mechanizm współdzielony przez wszystkie workery (np. dedykowany pojedynczy zapisujący worker, kolejkę lub blokadę międzyprocesową na wspólnym wolumenie).

## Zadanie 5.4

Zestaw stworzone wyżej taski w jeden potok przetwarzania i uruchom go. Przeskaluj worker obsługujący task scrapujący artykuły by używał 3 instancji

## Zadanie 5.5

Użyj narzędzia Flower, by monitorować pracę systemu, ilość workerów i stan kolejek
