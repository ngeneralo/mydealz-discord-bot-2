from time import perf_counter
from products import *

perf_start = perf_counter()
for prod in get_latest():
    print(prod)
perf_end = perf_counter()

print(f"Time: {perf_end-perf_start}s")
