import test_mod
import random
from time import perf_counter
from collections import Counter

start = perf_counter()

string = "smoooodles aa"
for r in range(100_000):
    result = test_mod.count_words(string)

# for r in range(100_000):
#     result = Counter(string)

# n = 10_000
# l = [random.randint(0, n) for _ in range(n)]

# print(list(sorted(l)))

print(f"Time taken: {(perf_counter() - start) *1000} miliseconds")
