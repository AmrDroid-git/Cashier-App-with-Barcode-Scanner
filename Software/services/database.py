import sqlite3
from datetime import datetime

DB_FILE = "db.sqlite"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            barcode TEXT UNIQUE,
            price REAL,
            quantity INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT,
            price REAL,
            quantity INTEGER,
            date TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL,
            date TEXT,
            filepath TEXT
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            barcode TEXT UNIQUE,
            price REAL,
            quantity_to_buy INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def add_product(name, barcode, price, quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, barcode, price, quantity) VALUES (?, ?, ?, ?)",
                (name, barcode, price, quantity))
    conn.commit()
    conn.close()

def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return products

def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def update_product(product_id, name, barcode, price, quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE products SET name = ?, barcode = ?, price = ?, quantity = ? WHERE id = ?",
                (name, barcode, price, quantity, product_id))
    conn.commit()
    conn.close()

def get_product_by_barcode(barcode):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    product = cur.fetchone()
    conn.close()
    return product

def record_sale(barcode, name, price, quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO sales (barcode, name, price, quantity, date) VALUES (?, ?, ?, ?, ?)",
                (barcode, name, price, quantity, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def record_facture(total, filepath):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO factures (total, date, filepath) VALUES (?, ?, ?)",
                (total, datetime.now().isoformat(), filepath))
    conn.commit()
    conn.close()

def get_sales_history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales ORDER BY date DESC")
    sales = cur.fetchall()
    conn.close()
    return sales

def get_facture_history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM factures ORDER BY date DESC")
    factures = cur.fetchall()
    conn.close()
    return factures

def delete_product_by_barcode(barcode):
    conn = get_connection()
    cur = conn.cursor()

    # Check if barcode exists
    cur.execute("SELECT 1 FROM products WHERE barcode = ?", (barcode,))
    result = cur.fetchone()

    if result is None:
        conn.close()
        raise ValueError(f"No product found with barcode: {barcode}")

    # If exists, delete it
    cur.execute("DELETE FROM products WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()



def clear_cart():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cart")
    conn.commit()
    conn.close()

def get_cart_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cart")
    items = cur.fetchall()
    conn.close()
    return items

def add_to_cart_or_increment(barcode):
    conn = get_connection()
    cur = conn.cursor()

    # Get available quantity
    cur.execute("SELECT quantity FROM products WHERE barcode = ?", (barcode,))
    product_qty_row = cur.fetchone()
    if product_qty_row is None:
        conn.close()
        return  # Product doesn't exist
    available_qty = product_qty_row[0]

    # Get current quantity in cart
    cur.execute("SELECT quantity_to_buy FROM cart WHERE barcode = ?", (barcode,))
    cart_row = cur.fetchone()

    if cart_row:
        new_qty = cart_row[0] + 1
        if new_qty > available_qty:
            conn.close()
            raise ValueError("Quantity to buy exceeds stock available.")
        cur.execute("UPDATE cart SET quantity_to_buy = ? WHERE barcode = ?", (new_qty, barcode))
    else:
        if 1 > available_qty:
            conn.close()
            raise ValueError("Not enough stock to add this product.")
        cur.execute("SELECT name, price FROM products WHERE barcode = ?", (barcode,))
        product = cur.fetchone()
        if product:
            name, price = product
            cur.execute(
                "INSERT INTO cart (name, barcode, price, quantity_to_buy) VALUES (?, ?, ?, ?)",
                (name, barcode, price, 1)
            )

    conn.commit()
    conn.close()


def decrement_stock_after_sale(cart_items):
    conn = get_connection()
    cur = conn.cursor()
    for _, name, barcode, price, quantity in cart_items:
        cur.execute("UPDATE products SET quantity = quantity - ? WHERE barcode = ?", (quantity, barcode))
    conn.commit()
    conn.close()


def cancel_sale(barcode, quantity, date):
    conn = get_connection()
    cur = conn.cursor()

    # 1. Delete sale line by barcode and exact datetime
    cur.execute("DELETE FROM sales WHERE barcode = ? AND date = ?", (barcode, date))

    # 2. Increment stock in products table
    cur.execute("UPDATE products SET quantity = quantity + ? WHERE barcode = ?", (quantity, barcode))

    conn.commit()
    conn.close()



def delete_facture_by_path(filepath):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM factures WHERE filepath = ?", (filepath,))
    conn.commit()
    conn.close()
