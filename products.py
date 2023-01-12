from bs4 import BeautifulSoup
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
        self.type = ""
        self.old_price = price_str_to_float(old_price)
        self.price = price_str_to_float(price)
        try:
            self.discount = int(discount)
        except:
            self.discount = 0

    def __repr__(self):
        text = self.url + "\n"
        text += f"Name: {self.name}\n"
        text += f"Old price: {float_to_price(self.old_price)}\n"
        text += f"New price: {float_to_price(self.price)}\n"
        text += f"Discount: -{self.discount}%\n"
        return text


def get_latest():
    main_url = "https://www.mydealz.de/new"

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "+\
            "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36 OPR/55.0.2994.61"
            }
    
    product_class = {"class": "threadGrid thread-clickRoot"}

    title_class = {
    "class": "cept-tt thread-link linkPlain thread-title--list js-thread-title"}

    price_class = {
    "class": "thread-price text--b cept-tp size--all-l size--fromW3-xl"}

    old_price_class = {
        "class": "mute--text text--lineThrough size--all-l size--fromW3-xl"}

    discount_class = {"class": "space--ml-1 size--all-l size--fromW3-xl"}

    try:
        html_text = requests.get(main_url, headers=header, timeout=20).text
    except requests.exceptions.RequestException as e:
        return None
    
    soup = BeautifulSoup(html_text, 'html.parser')

    for tag in soup.find_all("div", product_class,limit = 5):
        title = tag.find("a", title_class)
        name = title['title'][:100]
        url = title['href']
        price = tag.find("span", price_class)
        discount = tag.find("span", discount_class) 
        old_price = tag.find("span",old_price_class)
        if old_price:
            old_price = old_price.encode_contents().decode('utf-8')
            old_price = old_price.replace('.', '').replace('€', '').replace(',', '.')
        if price:
            price = price.encode_contents().decode('utf-8')
            price = price.replace('.', '').replace('€', '').replace(',', '.')
        if discount:
            discount = discount.encode_contents().decode('utf-8')
            discount = discount.replace('-', '').replace('%', '')
        yield Product(name, url, old_price, price, discount)


if __name__ == "__main__":
    for prod in get_latest():
        print(prod.name,prod.price)
        break