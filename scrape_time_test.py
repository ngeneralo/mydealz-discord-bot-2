import products
from time import perf_counter

perf_start = perf_counter()
latest = products.get_latest()
perf_end = perf_counter()
print(f"Time: {perf_end-perf_start}s")

for prod in latest:
    print(prod.name)