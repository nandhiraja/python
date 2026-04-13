CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    name TEXT,
    price REAL,
    last_updated TEXT
)
"""