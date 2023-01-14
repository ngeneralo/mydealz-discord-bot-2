import products
from time import perf_counter

perf_start = perf_counter()
products.get_latest()
print(f"Time: {perf_counter()-perf_start}s")