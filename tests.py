import test_mod
import random
from time import perf_counter
from collections import Counter

start = perf_counter()

string = "smoooodles aa"
# for r in range(100_000):
#     result = test_mod.count_words(string)

# for r in range(100_000):
#     result = Counter(string)

# n = 10_000
# l = [random.randint(0, n) for _ in range(n)]

# print(list(sorted(l)))


class Scale(float):
    def __mul__(self, value):

        return round(super().__mul__(value))

    def __rmul__(self, value):

        return round(super().__mul__(value))


def make_globals():
    local_vars = locals()
    print(local_vars)
    for var_name, var_value in local_vars.items():
        print(var_name)
        globals()[var_name] = var_value

def set_variables():
    var1 = "Hello, World!"
    var2 = 123
    var3 = [4, 5, 6]
    
    local_vars = locals()

    for var_name, var_value in local_vars.items():
        print(var_name)
        globals()[var_name] = var_value

set_variables()

print(var1)  
print(var2)  
print(var3)  

print(f"Time taken: {(perf_counter() - start) *1000} miliseconds")
