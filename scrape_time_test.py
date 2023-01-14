from time import perf_counter
import requests
from bs4 import BeautifulSoup

main_url = "https://www.mydealz.de/new"

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "+\
        "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36 OPR/55.0.2994.61"
        }

request_start = perf_counter()
try:
    html_text = requests.get(main_url, headers=header, timeout=20).text
except requests.exceptions.RequestException as e:
    print(e)
requests_end = perf_counter()
print(f"requests.get time: {requests_end-request_start}s")

parse_start = perf_counter()
soup = BeautifulSoup(html_text, 'html.parser')
parse_end = perf_counter()
print(f"Parse time: {parse_end-parse_start}s")