from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
import re
import requests
import sys

ua=UserAgent()
HDR = {'User-Agent': ua.random,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

def url_checker(url: str):
    url_pattern = re.compile(r"https://www.amazon.in/.*/dp/")
    match = re.match(url_pattern, url)
    if match:
        return True, url[match.end():match.end() + 10]
    return False, 0


def get_html(url: str):
    valid_url, asin = url_checker(url)
    if valid_url:
        response = requests.get(url, headers=HDR)
        html = response.content
        return html, asin

def extract_product_details(val_tuple):
    details = {"name": "", "price": None, "availability": True, "latest-check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    html, asin = val_tuple
    soup = BeautifulSoup(html, "html.parser")
    price = soup.find(id="priceblock_ourprice")
    title = soup.find(id="productTitle")

    if price is None:
        item_prices = soup.find("ul", class_="a-button-list")
        for prices in item_prices.find_all('li'):
            span_with_no_attrs = prices.find(class_=None)
            try:
                if span_with_no_attrs.text == "Paperback":
                    price = prices.find('span', class_="a-color-price")
                    break
            except AttributeError as e:
                continue
                
    try:
        details["name"] = title.text.strip()
        details["price"] = float(price.text.strip().strip(u'\u20B9').replace(',', '').replace(', ', ''))
    except AttributeError as e:
        price = None
        out_of_stock = soup.find(id="outOfStock")
        unavailable = out_of_stock.find('span', class_='a-color-price').text
        if unavailable == "Currently unavailable.":
            details["availability"] = False

    return details


if __name__ == "__main__":
    print(extract_product_details(get_html(sys.argv[1])))