import sqlite3
from datetime import datetime

DB_PATH  = 'Product.db'

def get_connection():
    return sqlite3.connect(DB_PATH)


def update_product(product ,conn):
    cur = conn.cursor()
    cur.execute("""
            INSERT INTO products (sku, name, price, last_updated)
            VALUES (?, ?, ?, ?)
            """, (
        product["sku"],
        product["name"],
        float(product["price"]),
         datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    
def get_products(date, connection ):
        cur = connection.cursor()
        cur.execute("SELECT * FROM products WHERE last_updated  = ?",
                    (date,)
                      )
        return {row[1]: {'id': row[0],'name':row[1],'price':row[2],'date':row[3]} for row in cur.fetchall()} 
