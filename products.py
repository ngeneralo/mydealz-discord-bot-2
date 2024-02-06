from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests


# converts float to euro price string "19,99€"
def float_to_price(x):
    euros = int(x)
    cents = int(100*(x-int(x)))
    if cents < 10:
        cents_str = "0" + str(cents)
    else:
        cents_str = str(cents)
    return f"{euros},{cents_str}€"

# tries to convert string into float, else retruns 0.0
def price_str_to_float(s:str):
    try:
        num = float(s)
    except:
        num =  0.0
    return num



class Product:
    def __init__(self, name:str, url:str, old_price:str, price:str, discount:str):
        self.name = name
        self.url = url
        self.product_code = url.split('-')[-1]
        self.type = ""
        self.old_price = price_str_to_float(old_price)
        self.price = price_str_to_float(price)
        try:
            self.discount = int(discount)
        except:
            self.discount = 0

    def __repr__(self):
        text  = f"{self.url}\n"
        text += f"Name: {self.name}\n"
        text += f"Old price: {float_to_price(self.old_price)}\n"
        text += f"New price: {float_to_price(self.price)}\n"
        text += f"Discount: -{self.discount}%\n"
        return text


def get_latest(limit:int = 5):
    main_url = "https://www.mydealz.de/new"

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "+\
            "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36 OPR/55.0.2994.61"
            }

    product_class = "threadGrid thread-clickRoot"
    title_class = "cept-tt thread-link linkPlain thread-title--list js-thread-title"
    price_class = "threadItemCard-price text--b thread-price size--all-l size--fromW3-xl space--mr-0"
    old_price_class = "mute--text text--lineThrough space--ml-1 size--all-l size--fromW3-xl"
    discount_class = "text--color-charcoal space--ml-1 size--all-l size--fromW3-xl"    
    
    try:
        options = Options()
        options.binary_location = '/usr/lib/chromium-browser/chromedriver'
        driver = webdriver.Chrome(options=options)
        driver.get(main_url)
        html_text = driver.page_source
    except requests.exceptions.RequestException as e:
        return None
    
    tree = html.fromstring(html_text)
    elements = tree.find_class(product_class)[:limit]

    for tag in elements:
        title = tag.find_class(title_class)
        if not title:
            continue
        name = str(title[0].attrib.get('title'))
        if len(name) > 200:
            name = name[:200]+'...'
        url = str(title[0].attrib.get('href'))
        
        price = tag.find_class(price_class)
        discount = tag.find_class(discount_class)
        old_price = tag.find_class(old_price_class)

        if old_price:
            old_price = str(old_price[0].text_content())
            old_price = old_price.replace('.', '').replace('€', '').replace(',', '.')
        if price:
            price = str(price[0].text_content())
            price = price.replace('.', '').replace('€', '').replace(',', '.')
        if discount:
            discount = str(discount[0].text_content())
            discount = discount.replace('-', '').replace('%', '')
        yield Product(name, url, old_price, price, discount)


if __name__ == "__main__":
    for prod in get_latest(limit=1):
        print(prod)
        print()