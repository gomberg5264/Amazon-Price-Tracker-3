import math
import logging
from src import db, async_mail, send_mail
from src.models import User, Products
from src.scraper import get_html, extract_product_details, main
from threading import Thread
from schedule import every, run_pending
import sys
from time import sleep

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s', filename='mails.log')

def get_products_list():
    products = Products.query.all()
    return products, len(products)

def check_product_price(slice):
    for i in slice:
        details = extract_product_details(get_html(i.url))
        item_price = details.get('price')
        if item_price is None:
            continue    
        if item_price <= i.expected_price:
            i.product_price = item_price
            db.session.commit()
            email = User.query.filter_by(username=i.user_id).first().email
            subject = "Item at price you wanted!"
            body = "The item {} is available at price {}!! Hurry now to buy it today! The link to the item - \n".format(i.product_name, i.expected_price)
            html = "<a href={}> Click here </a>".format(i.url)
            logging.warning("Mail sent to {}".format(email))
            print("Sent")
            async_mail(send_mail(subject=subject, recipient=email, body=body, html=html))
    sys.exit(1)

def check_threads():
    products, number = get_products_list()
    slice_len = math.ceil(number/5)
    db_check = []

    for i in range(5):
        if i * slice_len > number:
            break
        db_check.append(Thread(target=check_product_price, args=(products[i * slice_len: min((i + 1) * slice_len, number)],), name="check_product"))
    
    for i in db_check:
        i.start()

def loop():
    every(1).hour.do(check_threads)
    while True:
        run_pending()
        sleep(1)

if __name__ == "__main__":
    loop()