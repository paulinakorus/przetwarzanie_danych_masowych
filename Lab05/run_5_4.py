from celery import chain, group

from tasks import random_number, save_word, scrape_nth_word

# Potok: losowy numer n (5.1) -> n-te slowo losowego artykulu (5.2)
# -> zapis slowa do poematu (5.3). 30 potokow rownolegle.
pipelines = group(
    chain(random_number.s(), scrape_nth_word.s(), save_word.s())
    for _ in range(30)
)
res = pipelines()
print(res.get(timeout=300, propagate=False))
