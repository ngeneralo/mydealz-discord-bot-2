import products
from time import perf_counter

perf_start = perf_counter()
for prod in products.get_latest():
    print(prod.name)
print(f"Time: {perf_counter()-perf_start}s")