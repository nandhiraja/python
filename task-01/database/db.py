import sqlite3
from datetime import datetime
from database.db_model import CREATE_TABLE

DB_PATH  = 'Product.db'

def get_connection():
    return sqlite3.connect(DB_PATH)



def update_product(product):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(CREATE_TABLE)

    cur.execute("""
    INSERT INTO products (sku, name, price, last_updated)
    VALUES (?, ?, ?, ?)   ON CONFLICT(sku) DO UPDATE SET 
         price=excluded.price,
        last_updated=excluded.last_updated
    """, (
        product["sku"],
        product["name"],
        float(product["price"].replace("$", "")),
        datetime.now()
    ))

    conn.commit()
    conn.close()