from celery import group

from tasks import random_number

results = group(random_number.s() for _ in range(100))()
numbers = results.get(timeout=60)
print(len(numbers), numbers)
