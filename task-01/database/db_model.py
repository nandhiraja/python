CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    sku TEXT,
    name TEXT,
    price REAL,
    last_updated DATETIME
)
"""