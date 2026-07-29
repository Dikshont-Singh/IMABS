import sqlite3
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path('School-project/Database').resolve().parent

DATABASE_FOLDER = BASE_DIR / "Database"

# Create Database folder automatically
DATABASE_FOLDER.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_FOLDER / "inventory.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_FILE)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# CALCULATE STOCK STATUS
# ============================================================

def get_stock_status(quantity):

    if quantity <= 0:
        return "Out of Stock"

    elif quantity <= 10:
        return "Low Stock"

    else:
        return "In Stock"


# ============================================================
# ADD PRODUCT
# ============================================================

def add_product(sku, name, category, quantity, price):

    status = get_stock_status(quantity)

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO products
            (sku, name, category, quantity, price, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sku,
            name,
            category,
            quantity,
            price,
            status
        ))

        connection.commit()

        return True, "Product added successfully."

    except sqlite3.IntegrityError:

        return False, "This SKU already exists."

    finally:

        connection.close()


# ============================================================
# GET ALL PRODUCTS
# ============================================================

def get_products():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            sku,
            name,
            category,
            quantity,
            price,
            status
        FROM products
        ORDER BY id DESC
    """)

    products = cursor.fetchall()

    connection.close()

    return products


# ============================================================
# SEARCH PRODUCTS
# ============================================================

def search_products(search_text):

    connection = get_connection()
    cursor = connection.cursor()

    search = f"%{search_text}%"

    cursor.execute("""
        SELECT
            id,
            sku,
            name,
            category,
            quantity,
            price,
            status

        FROM products

        WHERE sku LIKE ?
           OR name LIKE ?
           OR category LIKE ?
           OR status LIKE ?

        ORDER BY id DESC
    """, (
        search,
        search,
        search,
        search
    ))

    products = cursor.fetchall()

    connection.close()

    return products


# ============================================================
# UPDATE PRODUCT
# ============================================================

def update_product(
    product_id,
    sku,
    name,
    category,
    quantity,
    price
):

    status = get_stock_status(quantity)

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE products

            SET sku = ?,
                name = ?,
                category = ?,
                quantity = ?,
                price = ?,
                status = ?

            WHERE id = ?
        """, (
            sku,
            name,
            category,
            quantity,
            price,
            status,
            product_id
        ))

        connection.commit()

        return True, "Product updated successfully."

    except sqlite3.IntegrityError:

        return False, "This SKU already exists."

    finally:

        connection.close()


# ============================================================
# DELETE PRODUCT
# ============================================================

def delete_product(product_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM products
        WHERE id = ?
    """, (product_id,))

    connection.commit()
    connection.close()


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def get_dashboard_stats():

    connection = get_connection()
    cursor = connection.cursor()

    # Total stock value
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0)
        FROM products
    """)

    total_stock_value = cursor.fetchone()[0]

    # Low stock
    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE quantity > 0
        AND quantity <= 10
    """)

    low_stock = cursor.fetchone()[0]

    # Total products
    cursor.execute("""
        SELECT COUNT(*)
        FROM products
    """)

    total_products = cursor.fetchone()[0]

    connection.close()

    return {
        "total_stock_value": total_stock_value,
        "low_stock": low_stock,
        "total_products": total_products
    }


# ============================================================
# TEST DATABASE
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")
    print(f"Database location:")
    print(DATABASE_FILE)