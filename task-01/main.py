from scraper.extractor import scrape_site

from database.db import get_connection ,update_product ,get_products
from settings import URL
from datetime import datetime
from database.db_model import CREATE_TABLE
from report import generate_report
import random
connection = get_connection()
date_now = ''

def init_db():
    cur =  connection.cursor()
    cur.execute(CREATE_TABLE)
    connection.commit()



def get_items(URL):
    global date_now
    current_product = scrape_site(URL,1)
    date_now =  datetime.now().strftime("%Y-%m-%d %H:%M")
    for item in current_product:
        random_value = random.choice([0,1,5,9])
        item['price']= item['price'].replace("£", "")
        item['price'] = float(item['price'])+random_value

        update_product(item,connection)
        connection.commit()

    print('insert done')


init_db()
get_items(URL)

print(date_now)
with open ('./history.txt','a') as hist:
    hist.write(date_now+'\n')
    
lastest_product=get_products(date_now,connection)
previous = get_products('2026-04-14 10:23' ,connection)


print("Generated_Report : ",generate_report(lastest_product,previous))
