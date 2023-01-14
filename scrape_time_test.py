from time import perf_counter
from lxml import html
from bs4 import BeautifulSoup

import requests

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
tree = html.fromstring(html_text)
parse_end = perf_counter()
print(f"lxml parse time: {parse_end-parse_start}s")


product_class = {"class": "threadGrid thread-clickRoot"}
title_class = {"class": "cept-tt thread-link linkPlain thread-title--list js-thread-title"}

elements = tree.find_class(product_class["class"])

tag = elements[1].find_class(title_class["class"])

for a_elem in tag:
    print(a_elem.attrib['title'])
    print(a_elem.attrib['href'])

