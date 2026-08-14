import sqlite3
import csv
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

# School-project folder
BASE_DIR = Path(__file__).resolve().parent

# Database folder
DATABASE_DIR = BASE_DIR / "Database"

# Create Database folder if it doesn't exist
DATABASE_DIR.mkdir(exist_ok=True)

# SQLite database file
DATABASE_FILE = DATABASE_DIR / "inventory.db"


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
# STOCK STATUS
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

def add_product(
    sku,
    name,
    category,
    quantity,
    price
):

    connection = get_connection()
    cursor = connection.cursor()

    status = get_stock_status(quantity)

    try:

        cursor.execute("""
            INSERT INTO products
            (
                sku,
                name,
                category,
                quantity,
                price,
                status
            )

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

        return False, "SKU already exists."

    except Exception as error:

        return False, str(error)

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

        WHERE
            sku LIKE ?
            OR name LIKE ?
            OR category LIKE ?

        ORDER BY id DESC
    """, (
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

    connection = get_connection()
    cursor = connection.cursor()

    status = get_stock_status(quantity)

    try:

        cursor.execute("""
            UPDATE products

            SET
                sku = ?,
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

        return False, "Another product already uses this SKU."

    except Exception as error:

        return False, str(error)

    finally:

        connection.close()


# ============================================================
# DELETE PRODUCT
# ============================================================

def delete_product(product_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM products
            WHERE id = ?
        """, (product_id,))

        connection.commit()

        return True, "Product deleted successfully."

    except Exception as error:

        return False, str(error)

    finally:

        connection.close()


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def get_dashboard_stats():

    connection = get_connection()
    cursor = connection.cursor()

    # Total stock value
    cursor.execute("""
        SELECT
            COALESCE(SUM(quantity * price), 0)

        FROM products
    """)

    total_value = cursor.fetchone()[0]


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


    # Out of stock
    cursor.execute("""
        SELECT COUNT(*)

        FROM products

        WHERE quantity <= 0
    """)

    out_of_stock = cursor.fetchone()[0]


    connection.close()


    return {
        "total_value": total_value,
        "low_stock": low_stock,
        "total_products": total_products,
        "out_of_stock": out_of_stock
    }


# ============================================================
# IMPORT CSV
# ============================================================

def import_products_from_csv(file_path):

    added = 0
    skipped = 0
    errors = []

    connection = get_connection()
    cursor = connection.cursor()

    try:

        with open(
            file_path,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            required_columns = {
                "SKU",
                "Product Name",
                "Category",
                "Quantity",
                "Price"
            }

            # Check columns
            if not required_columns.issubset(
                set(reader.fieldnames or [])
            ):

                return (
                    0,
                    0,
                    [
                        "Incorrect CSV format.",
                        "Required columns:",
                        "SKU, Product Name, Category, Quantity, Price"
                    ]
                )


            for row_number, row in enumerate(
                reader,
                start=2
            ):

                try:

                    sku = row["SKU"].strip()

                    name = row["Product Name"].strip()

                    category = row["Category"].strip()

                    quantity = int(
                        row["Quantity"]
                    )

                    price = float(
                        row["Price"]
                    )


                    # Validation

                    if not sku:
                        raise ValueError(
                            "SKU is empty."
                        )

                    if not name:
                        raise ValueError(
                            "Product name is empty."
                        )

                    if not category:
                        raise ValueError(
                            "Category is empty."
                        )

                    if quantity < 0:
                        raise ValueError(
                            "Quantity cannot be negative."
                        )

                    if price < 0:
                        raise ValueError(
                            "Price cannot be negative."
                        )


                    status = get_stock_status(
                        quantity
                    )


                    cursor.execute("""
                        INSERT INTO products
                        (
                            sku,
                            name,
                            category,
                            quantity,
                            price,
                            status
                        )

                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        sku,
                        name,
                        category,
                        quantity,
                        price,
                        status
                    ))


                    added += 1


                except sqlite3.IntegrityError:

                    skipped += 1

                    errors.append(
                        f"Row {row_number}: "
                        f"SKU '{row.get('SKU', '')}' "
                        f"already exists."
                    )


                except Exception as error:

                    skipped += 1

                    errors.append(
                        f"Row {row_number}: {error}"
                    )


        connection.commit()


    except Exception as error:

        connection.rollback()

        return (
            added,
            skipped,
            [str(error)]
        )


    finally:

        connection.close()


    return added, skipped, errors


# ============================================================
# EXPORT CSV
# ============================================================

def export_products_to_csv(file_path):

    products = get_products()

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "SKU",
            "Product Name",
            "Category",
            "Quantity",
            "Price",
            "Status"
        ])


        for product in products:

            writer.writerow(product)


    return len(products)


# ============================================================
# CREATE DATABASE WHEN THIS FILE IS RUN
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")

    print(
        f"Database location:\n{DATABASE_FILE}"
    )