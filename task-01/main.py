from scraper.extractor import scrape_site

from database.db import get_connection ,update_product ,get_products
from settings import URL
from datetime import datetime
from database.db_model import CREATE_TABLE

connection = get_connection()
date_now = ''

def init_db():
    cur =  connection.cursor()
    cur.execute(CREATE_TABLE)
    connection.commit()



def get_items(URL):
    global date_now
    current_product = scrape_site(URL)
    date_now =  datetime.now().strftime("%Y-%m-%d %H:%M")
    for item in current_product:
        update_product(item,connection)
        connection.commit()

    print('insert done')


init_db()
get_items(URL)

print(date_now)

lastest_product=get_products(date_now,connection)
print(lastest_product)