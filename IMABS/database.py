import csv
import os
import sqlite3
import sys
from pathlib import Path

# ============================================================
# PERSISTENT DATABASE LOCATION (NEXT TO .EXE OR MAIN.PY)
# ============================================================
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

DB_FOLDER = APP_DIR / "Database"
DB_PATH = DB_FOLDER / "inventory.db"

# Ensure directory exists immediately
DB_FOLDER.mkdir(parents=True, exist_ok=True)

LOW_STOCK_THRESHOLD = 10


def get_connection():
    """Return SQLite connection pointing to APP_DIR/Database/inventory.db."""
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    # Using DELETE mode avoids WAL checkpoint lock bugs when apps close unexpectedly
    try:
        conn.execute("PRAGMA journal_mode=DELETE;")
    except sqlite3.Error:
        pass

    try:
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
    except sqlite3.Error:
        pass

    return conn


def get_low_stock_threshold() -> int:
    """Fetch the configured low-stock threshold from settings (default 10)."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT value FROM app_settings WHERE key = 'low_stock_threshold'"
            )
            row = cur.fetchone()
            if row and row[0] is not None:
                return max(1, int(float(row[0])))
    except Exception:
        pass
    return LOW_STOCK_THRESHOLD


def compute_status(quantity: int, threshold: int = None) -> str:
    """Compute stock status string from quantity."""
    limit = threshold if threshold is not None else get_low_stock_threshold()
    if quantity <= 0:
        return "Out of Stock"
    if quantity <= limit:
        return "Low Stock"
    return "In Stock"


def initialize_database():
    """Ensure all required tables and indices exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'In Stock'
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT DEFAULT '',
                payment_method TEXT NOT NULL DEFAULT 'Cash',
                subtotal REAL NOT NULL DEFAULT 0.0,
                discount_pct REAL NOT NULL DEFAULT 0.0,
                discount_amount REAL NOT NULL DEFAULT 0.0,
                tax_pct REAL NOT NULL DEFAULT 0.0,
                tax_amount REAL NOT NULL DEFAULT 0.0,
                grand_total REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER,
                sku TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        conn.commit()


def add_product(sku, name, category, quantity, price):
    """Add a new product to the database."""
    status = compute_status(int(quantity))
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO products (sku, name, category, quantity, price, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sku.strip(), name.strip(), category.strip(), int(quantity), float(price), status),
            )
            conn.commit()
        return True, f"Product '{name}' added successfully."
    except sqlite3.IntegrityError:
        return False, f"SKU '{sku}' already exists."
    except Exception as exc:
        return False, f"Database error: {exc}"


def get_products():
    """Retrieve all products ordered by ID descending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, sku, name, category, quantity, price, status
            FROM products
            ORDER BY id DESC
            """
        )
        return cursor.fetchall()


def search_products(query):
    """Search products by SKU, name, category, or status."""
    pattern = f"%{query.strip()}%"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, sku, name, category, quantity, price, status
            FROM products
            WHERE sku LIKE ? OR name LIKE ? OR category LIKE ? OR status LIKE ?
            ORDER BY id DESC
            """,
            (pattern, pattern, pattern, pattern),
        )
        return cursor.fetchall()


def update_product(product_id, sku, name, category, quantity, price):
    """Update an existing product by ID."""
    status = compute_status(int(quantity))
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE products
                SET sku = ?, name = ?, category = ?, quantity = ?, price = ?, status = ?
                WHERE id = ?
                """,
                (
                    sku.strip(),
                    name.strip(),
                    category.strip(),
                    int(quantity),
                    float(price),
                    status,
                    int(product_id),
                ),
            )
            if cursor.rowcount == 0:
                return False, "Product not found."
            conn.commit()
        return True, f"Product '{name}' updated successfully."
    except sqlite3.IntegrityError:
        return False, f"SKU '{sku}' is already in use by another product."
    except Exception as exc:
        return False, f"Database error: {exc}"


def delete_product(product_id):
    """Delete a product by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (int(product_id),))
            if cursor.rowcount == 0:
                return False, "Product not found."
            conn.commit()
        return True, "Product deleted successfully."
    except Exception as exc:
        return False, f"Database error: {exc}"


def get_dashboard_stats():
    """Return aggregate inventory statistics using a single SQL query."""
    threshold = get_low_stock_threshold()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(quantity * price), 0.0),
                COALESCE(SUM(CASE WHEN quantity > 0 AND quantity <= ? THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN quantity <= 0 THEN 1 ELSE 0 END), 0)
            FROM products
            """,
            (threshold,),
        )
        row = cursor.fetchone()
        return {
            "total_products": row[0] if row else 0,
            "total_value": float(row[1]) if row else 0.0,
            "low_stock": row[2] if row else 0,
            "out_of_stock": row[3] if row else 0,
        }

def import_products_from_csv(file_path):
    """
    Safely import products from a CSV file.
    Always returns: (added_count, skipped_count, list_of_error_strings)
    """
    added = 0
    skipped = 0
    errors = []
    
    if not file_path or not os.path.isfile(file_path):
        return 0, 0, ["Selected file does not exist."]

    try:
        threshold = get_low_stock_threshold()

        with open(file_path, mode="r", encoding="utf-8-sig", errors="replace", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not reader.fieldnames:
                return 0, 0, ["CSV file is empty or missing header columns."]

            # Build case-insensitive header mapping
            header_map = {str(h).strip().lower(): h for h in reader.fieldnames if h}

            def get_col(row_dict, *candidates):
                for c in candidates:
                    if c in header_map:
                        val = row_dict.get(header_map[c])
                        return str(val).strip() if val is not None else ""
                return ""

            with get_connection() as conn:
                cursor = conn.cursor()
                for idx, row in enumerate(reader, start=2):
                    sku = get_col(row, "sku", "product sku", "code", "barcode", "id")
                    name = get_col(row, "name", "product name", "product", "item", "title")
                    category = get_col(row, "category", "cat", "group", "type") or "General"
                    qty_str = get_col(row, "quantity", "qty", "stock", "count")
                    price_str = get_col(row, "price", "unit price", "rate", "cost", "mrp")

                    # Clean currency symbols and commas
                    price_str = price_str.replace("₹", "").replace("$", "").replace(",", "").strip()
                    qty_str = qty_str.replace(",", "").strip()

                    # Check required fields
                    if not sku or not name or qty_str == "" or price_str == "":
                        skipped += 1
                        errors.append(f"Row {idx}: Missing essential fields (SKU, Name, Quantity, or Price).")
                        continue

                    # Parse numbers safely
                    try:
                        qty = int(float(qty_str))
                        price = float(price_str)
                        if qty < 0 or price < 0:
                            raise ValueError()
                    except ValueError:
                        skipped += 1
                        errors.append(f"Row {idx} ('{sku}'): Invalid number format for quantity ('{qty_str}') or price ('{price_str}').")
                        continue

                    # Check for duplicate SKU before inserting
                    cursor.execute("SELECT 1 FROM products WHERE sku = ?", (sku,))
                    if cursor.fetchone():
                        skipped += 1
                        errors.append(f"Row {idx}: SKU '{sku}' already exists.")
                        continue

                    status = compute_status(qty, threshold)

                    cursor.execute(
                        """
                        INSERT INTO products (sku, name, category, quantity, price, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (sku, name, category, qty, price, status),
                    )
                    added += 1

                conn.commit()

    except Exception as exc:
        errors.append(f"File reading error: {str(exc)}")

    # Always return 3 items, never None
    return added, skipped, errors

def export_products_to_csv(file_path):
    """Export all products to a CSV file."""
    products = get_products()
    with open(file_path, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "SKU", "Product Name", "Category", "Quantity", "Price", "Status"])
        writer.writerows(products)
    return len(products)