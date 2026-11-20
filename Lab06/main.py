import os
import random
import secrets
import socket
import string
import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# --------------------------------------------------------------------------- #
# Pomocnicze
# --------------------------------------------------------------------------- #
def get_session(app_name: str) -> SparkSession:
    spark_master_url = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(spark_master_url)
        # workery mają 2G / 1 rdzeń - jeden executor na workera
        .config("spark.executor.memory", "1g")
        .config("spark.executor.cores", "1")
    )
    if spark_master_url.startswith("spark://"):
        # tryb client: executory muszą móc połączyć się z driverem (ten kontener)
        builder = (
            builder
            .config("spark.driver.host", socket.gethostbyname(socket.gethostname()))
            .config("spark.driver.bindAddress", "0.0.0.0")
        )
    return builder.getOrCreate()


def env_int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


def base_seed() -> int:
    """Ziarno bazowe wybierane RAZ, na driverze.

    Dzięki temu ponowne obliczenie partycji (retry zadania, utrata executora,
    speculative execution) daje dokładnie te same dane, a jednocześnie każde
    uruchomienie programu daje inne liczby (chyba że ustawiono BASE_SEED).
    """
    env = os.getenv("BASE_SEED")
    return int(env) if env else secrets.randbits(63)


def partition_rng(seed: int, partition_index: int) -> random.Random:
    """Niezależny generator dla partycji.

    random.Random(str) hashuje napis (SHA-512), więc ziarna "seed:0", "seed:1", ...
    dają całkowicie niepowiązane strumienie - w przeciwieństwie do seed + idx,
    gdzie sąsiednie ziarna bywają silnie skorelowane w słabszych generatorach.
    """
    return random.Random(f"{seed}:{partition_index}")


def keep_ui_alive() -> None:
    seconds = env_int("KEEP_ALIVE_SECONDS", 0)
    if seconds > 0:
        print(f"[info] Spark UI aplikacji: http://localhost:4040 - czekam {seconds}s ...", flush=True)
        time.sleep(seconds)


def split_sizes(total: int, parts: int) -> list:
    """Dzieli total na parts możliwie równych kawałków (suma == total)."""
    base, rem = divmod(total, parts)
    return [base + (1 if i < rem else 0) for i in range(parts)]


# --------------------------------------------------------------------------- #
# Przykład
# --------------------------------------------------------------------------- #
def example() -> None:
    spark = get_session("Example app")
    print(f"[info] Spark version: {spark.version}")

    df = spark.createDataFrame(
        data=[
            (1, "Alice"),
            (2, "Bob"),
            (3, "Charlie"),
        ],
        schema=["id", "name"],
    )

    df.show()

    print(f"Total rows: {df.count()}")

    keep_ui_alive()
    spark.stop()


# --------------------------------------------------------------------------- #
# Zadanie 6.2 - 10 000 000 losowych double w 10 partycjach
# --------------------------------------------------------------------------- #
def generate_numbers() -> None:
    total = env_int("TOTAL_NUMBERS", 10_000_000)
    partitions = env_int("NUM_PARTITIONS", 10)

    spark = get_session("Number generator app")
    sc = spark.sparkContext

    seed = base_seed()  # jedno ziarno bazowe, wylosowane na driverze
    sizes = split_sizes(total, partitions)
    print(f"[info] base seed = {seed}, liczb na partycję = {sizes}")

    def generate_partition(index, _iterator):
        # index = numer partycji -> unikalne ziarno dla każdej partycji
        rng = partition_rng(seed, index)
        for _ in range(sizes[index]):
            yield rng.random()

    def summarize_partition(index, iterator):
        # jedno przejście po danych: liczba, suma, min, max, pierwsza wartość
        count, total_sum, lo, hi, first = 0, 0.0, float("inf"), float("-inf"), None
        for x in iterator:
            if first is None:
                first = x
            count += 1
            total_sum += x
            lo = x if x < lo else lo
            hi = x if x > hi else hi
        yield (index, count, total_sum, lo, hi, first)

    # 1) lista 10 liczb (po jednej na partycję), 2) rozproszenie na 10 partycji,
    # 3) zmapowanie każdej partycji na zadaną liczbę losowych double
    numbers = (
        sc.parallelize(list(range(partitions)), partitions)
        .mapPartitionsWithIndex(generate_partition)
    )

    stats = numbers.mapPartitionsWithIndex(summarize_partition).collect()

    print(f"{'part':>4} {'count':>10} {'mean':>10} {'min':>12} {'max':>12} {'first value':>14}")
    for index, count, s, lo, hi, first in sorted(stats):
        print(f"{index:>4} {count:>10} {s / count:>10.6f} {lo:>12.3e} {hi:>12.6f} {first:>14.10f}")

    n = sum(x[1] for x in stats)
    mean = sum(x[2] for x in stats) / n
    firsts = [x[5] for x in stats]
    print(f"[wynik] razem wygenerowano: {n} liczb (oczekiwano {total})")
    print(f"[wynik] średnia = {mean:.6f} (oczekiwana ~0.5), "
          f"min = {min(x[3] for x in stats):.3e}, max = {max(x[4] for x in stats):.6f}")
    print(f"[wynik] różnych pierwszych wartości partycji: {len(set(firsts))} z {partitions} "
          f"(przy tym samym ziarnie byłaby 1)")

    keep_ui_alive()
    spark.stop()


# --------------------------------------------------------------------------- #
# Zadanie 6.3a - 1 000 000 losowych stringów o losowej długości -> dysk
# --------------------------------------------------------------------------- #
def create_random_strings() -> None:
    count = env_int("STRINGS_COUNT", 1_000_000)
    min_len = env_int("STRING_MIN_LEN", 5)
    max_len = env_int("STRING_MAX_LEN", 50)
    partitions = env_int("STRINGS_PARTITIONS", 10)
    path = os.getenv("STRINGS_PATH", "/data/random_strings")

    if min_len < 1 or max_len < min_len:
        raise ValueError(f"Niepoprawny przedział długości: [{min_len}, {max_len}]")

    spark = get_session("Create random strings app")
    sc = spark.sparkContext

    seed = base_seed()
    sizes = split_sizes(count, partitions)
    alphabet = string.ascii_letters + string.digits
    print(f"[info] base seed = {seed}, {count} stringów, długość [{min_len}, {max_len}], "
          f"{partitions} partycji, zapis do {path}")

    def generate_partition(index, _iterator):
        rng = partition_rng(seed, index)
        for _ in range(sizes[index]):
            length = rng.randint(min_len, max_len)
            yield "".join(rng.choices(alphabet, k=length))

    strings = (
        sc.parallelize(list(range(partitions)), partitions)
        .mapPartitionsWithIndex(generate_partition)
    )

    # DDL "string" -> jedna kolumna "value"; każdy string w osobnej linii pliku tekstowego
    df = spark.createDataFrame(strings, "string")
    df.write.mode("overwrite").text(path)

    print(f"[wynik] zapisano {count} stringów do {path}")

    keep_ui_alive()
    spark.stop()


# --------------------------------------------------------------------------- #
# Zadanie 6.3b - wczytanie zapisanych danych i policzenie znaków
# --------------------------------------------------------------------------- #
def count_characters() -> None:
    path = os.getenv("STRINGS_PATH", "/data/random_strings")

    spark = get_session("Count characters app")

    df = spark.read.text(path)  # kolumna "value", jeden wiersz = jeden string
    lengths = df.select(F.length("value").alias("len"))

    row = lengths.agg(
        F.count("len").alias("strings"),
        F.sum("len").alias("chars"),
        F.min("len").alias("min_len"),
        F.max("len").alias("max_len"),
        F.avg("len").alias("avg_len"),
    ).first()

    print(f"[wynik] wczytano z {path}")
    if not row["strings"]:
        spark.stop()
        sys.exit(f"Brak danych w {path} - najpierw uruchom zadanie 'strings'.")
    print(f"[wynik] liczba stringów : {row['strings']}")
    print(f"[wynik] liczba znaków   : {row['chars']}")
    print(f"[wynik] długość min/max : {row['min_len']} / {row['max_len']}, średnia {row['avg_len']:.3f}")

    keep_ui_alive()
    spark.stop()


# --------------------------------------------------------------------------- #
TASKS = {
    "example": example,
    "numbers": generate_numbers,
    "strings": create_random_strings,
    "count": count_characters,
}


def main():
    selected = sys.argv[1] if len(sys.argv) > 1 else "all"
    if selected == "all":
        for task in TASKS.values():
            task()
    elif selected in TASKS:
        TASKS[selected]()
    else:
        sys.exit(f"Nieznane zadanie '{selected}'. Dostępne: {', '.join(TASKS)}, all")


if __name__ == "__main__":
    main()