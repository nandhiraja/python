import sqlite3
import os
import random
from datetime import date, timedelta

os.makedirs('data', exist_ok=True)
db_path = 'data/sales.db'

def setup():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date DATE,
        region TEXT,
        revenue REAL,
        units INTEGER
    )
    ''')
    
    cursor.execute("DELETE FROM sales")
    
    regions = ['North', 'South', 'East', 'West']
    
    start_date = date(2025, 11, 1)
    end_date = date(2026, 2, 28)
    
    delta = end_date - start_date
    
    means = {'North': 12000, 'South': 10000, 'East': 11000, 'West': 8000}
    
    for i in range(delta.days + 1):
        curr_date = start_date + timedelta(days=i)
        
        is_jan = curr_date.year == 2026 and curr_date.month == 1
        is_dec = curr_date.year == 2025 and curr_date.month == 12
        
        for r in regions:
            daily_rev = max(500, random.gauss(means[r], means[r] * 0.2))
            
            if r == 'West' and is_jan:
                daily_rev *= 0.6
                
            if r == 'West' and is_dec:
                daily_rev *= 1.2
            
            units = int(max(1, daily_rev / random.uniform(200, 500)))
            
            cursor.execute('''
            INSERT INTO sales (sale_date, region, revenue, units) 
            VALUES (?, ?, ?, ?)
            ''', (curr_date.strftime("%Y-%m-%d"), r, round(daily_rev, 2), units))
            
    conn.commit()
    conn.close()
    print("Database setup complete. Data populated in data/sales.db")

if __name__ == "__main__":
    setup()
