import test_mod
import random
from time import perf_counter
from collections import Counter
from sys import argv
import os, sys
from datetime import datetime
start = perf_counter()

print(sys.executable, argv, argv[0], "python" in os.path.basename(sys.executable), 'python' in os.path.basename(argv[0]))
string = "smoooodles aa"
# for r in range(100_000):
#     result = test_mod.count_words(string)

# for r in range(100_000):
#     result = Counter(string)

# n = 10_000
# l = [random.randint(0, n) for _ in range(n)]

# random.seed(datetime.now().microsecond)
# random.seed(1)
print(random.random())
print(f"Time taken: {(perf_counter() - start) *1000} miliseconds")
