import fcntl
import os
import random
import re

import requests
from bs4 import BeautifulSoup
from celery import Celery

BROKER = os.environ.get("CELERY_BROKER", "amqp://guest:guest@rabbitmq//")
BACKEND = os.environ.get("CELERY_BACKEND", "redis://redis:6379/0")

app = Celery("tasks", broker=BROKER, backend=BACKEND)
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True
app.conf.task_routes = {
    "tasks.scrape_nth_word": {"queue": "scraper"},
    "tasks.save_word": {"queue": "poem"},
}

WIKI_RANDOM = "https://pl.wikipedia.org/wiki/Special:Random"
HEADERS = {"User-Agent": "PWr-Lab5-Celery/1.0 (student lab; requests)"}
POEM_FILE = os.environ.get("POEM_FILE", "/data/poem.txt")
WORD_RE = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")
WORDS_PER_LINE = 5


# Zadanie 5.1
@app.task
def random_number():
    return random.randint(0, 200)


# Zadanie 5.2 -- numerowanie slow od 0 (n=0 to pierwsze slowo artykulu),
# pasuje do zakresu [0; 200] z zadania 5.1
def _fetch_words():
    resp = requests.get(WIKI_RANDOM, headers=HEADERS, timeout=15)
    resp.raise_for_status()  # bledy HTTP -> wyjatek
    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.select_one("#mw-content-text")
    if content is None:
        return []

    for tag in content.select("sup.reference, style, script, .mw-editsection"):
        tag.decompose()

    text = " ".join(p.get_text() for p in content.find_all("p"))
    return WORD_RE.findall(text)


@app.task(bind=True, autoretry_for=(requests.RequestException,),
          retry_backoff=True, max_retries=3)
def scrape_nth_word(self, n):
    if n < 0:
        raise ValueError("n musi byc >= 0 (numerowanie od 0)")
    # zbyt krotki artykul -> losujemy kolejny (max 10 prob)
    for _ in range(10):
        words = _fetch_words()
        if len(words) > n:
            return words[n]
    raise ValueError(f"nie znaleziono artykulu z co najmniej {n + 1} slowami")


# Zadanie 5.3 -- zapis chroniony blokada miedzyprocesowa (flock) na wspolnym
# wolumenie; dodatkowo task idzie do kolejki 'poem' obslugiwanej przez
# jednego workera (-c 1).
@app.task
def save_word(word):
    os.makedirs(os.path.dirname(POEM_FILE), exist_ok=True)
    with open(POEM_FILE, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            content = f.read()
            last = content.split("\n")[-1].split()
            if not last:
                f.write(word)
            elif len(last) >= WORDS_PER_LINE:
                f.write("\n" + word)
            else:
                f.write(" " + word)
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return f"zapisano {word}"
