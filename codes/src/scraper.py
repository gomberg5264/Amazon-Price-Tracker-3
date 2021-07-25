from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
import re
import requests
from typing import Dict, Tuple

#User-Agent is a header for GET request to a web-server, which tells the remote server that the request is coming from a browser and 
#it's not automated.
ua = UserAgent()
HDR = {'User-Agent': ua.random,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

def url_checker(url: str)->Tuple:
    """
    Function to validate the url. It checks whether the url is of an amazon product or not.
    """
    url_pattern = re.compile(r"https://www.amazon.in/.*/dp/")
    match = re.match(url_pattern, url)
    if match:
        return True, url[match.end():match.end() + 10]
    return False, None


def get_html(url: str)->Tuple:
    """
    Fetches the HTML page by sending a GET request. Returns the HTML content and the ASIN of the product
    """
    valid_url, asin = url_checker(url)
    if valid_url:
        response = requests.get(url, headers=HDR)
        html = response.content
        return html, asin, url
    return None, None, url


def extract_product_details(val_tuple: tuple)->Dict:
    """
    Returns the product details, including the name, current price and availability.
    """
    details = { "asin": None,
                "name": "", 
                "url": "",
                "price": None, 
                "availability": True, 
                "last-check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    html, asin, url = val_tuple
    details["asin"] = asin
    details["url"] = url
    if not html:
        return details
            
    soup = BeautifulSoup(html, "html.parser")
    price = soup.find(id="priceblock_ourprice")
    title = soup.find(id="productTitle")

    #If price is None, then most likely it is an amazon page for books, where different prices are listed for different copies like 
    #kindle, ebook, paperback
    if price is None:
        item_prices = soup.find("ul", class_="a-button-list")
        
        #Try except block is to check if multiple prices exist. Here I am only considering Paperback, but others can be considered with
        #a little modification
        try:
            for prices in item_prices.find_all('li'):
                span_with_no_attrs = prices.find(class_=None)
                try:
                    if span_with_no_attrs.text == "Paperback":
                        price = prices.find('span', class_="a-color-price")
                        break
                except AttributeError as e:
                    continue
        except AttributeError:
            pass
                
    try:
        details["name"] = title.text.strip()
        details["price"] = float(price.text.strip().strip(u'\u20B9').replace(',', '').replace(', ', ''))
    except AttributeError as e:
        price = None

        #In this block we check if the product is out of stock
        out_of_stock = soup.find(id="outOfStock")
        try:
            unavailable = out_of_stock.find('span', class_='a-color-price').text
            if unavailable == "Currently unavailable.":
                details["availability"] = False
        except AttributeError:
            #If outOfStock attribute not found, we can conclude that the url entered is not of a valid webpage
            
            details["availability"] = False
            print("Webpage not Valid")

    return details

def main():
    url = input()
    target_price = int(input())
    details = extract_product_details(get_html(url))
    if details["price"] <= target_price:
        print("The product is cheaper! Buy it now: ", details["url"]) 

main()