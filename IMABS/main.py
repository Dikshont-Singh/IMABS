<<<<<<< HEAD
=======
# IMPORTS
import sys
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
import csv
import os
import shutil
import sqlite3
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

<<<<<<< HEAD
BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
for p in (str(BASE_DIR.parent), str(BASE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

=======
# PATH 
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import database as _db_module
from database import (
    add_product,
    delete_product,
    export_products_to_csv,
    get_dashboard_stats,
    get_products,
    import_products_from_csv,
    initialize_database,
    search_products,
    update_product,
)

NAVY, NAVY_HOVER = "#172554", "#243B78"
BLUE, BLUE_HOVER = "#2563EB", "#1D4ED8"
GREEN, GREEN_HOVER = "#0F766E", "#115E59"
RED, RED_HOVER = "#DC2626", "#B91C1C"
ORANGE, ORANGE_HOVER = "#D97706", "#B45309"
GRAY, GRAY_HOVER = "#64748B", "#475569"
PAGE_BG, WHITE, BORDER, TEXT, MUTED = "#F4F6FA", "#FFFFFF", "#E2E8F0", "#0F172A", "#64748B"
CHART_PALETTE = ["#2563EB", "#0F766E", "#1E40AF", "#0D9488", "#3B82F6", "#D97706", "#64748B"]

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def _format_datetime_12h(value) -> str:
    if not value:
        return ""
    s = str(value).strip()
    for fmt in (
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%d/%m/%Y %I:%M:%S %p") if "%H" in fmt or "%I" in fmt else dt.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return s


def _ensure_writable_sqlite_path() -> Path:
<<<<<<< HEAD
    candidates = [BASE_DIR / "Database" / "inventory.db"]
=======
    
    script_dir = Path(__file__).resolve().parent
    candidates = []
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    if hasattr(_db_module, "DB_PATH"):
        p = Path(getattr(_db_module, "DB_PATH"))
        if p not in candidates:
            candidates.insert(0, p)
    candidates.append(BASE_DIR / "inventory.db")
    if local_app := os.environ.get("LOCALAPPDATA"):
        candidates.append(Path(local_app) / "IMABS" / "Database" / "inventory.db")
    candidates.extend([Path.home() / "IMABS_Data" / "inventory.db", Path(tempfile.gettempdir()) / "IMABS" / "inventory.db"])

    for cand in candidates:
        try:
<<<<<<< HEAD
            cand.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(cand)) as conn:
                conn.execute("PRAGMA journal_mode=MEMORY;")
                conn.execute("CREATE TABLE IF NOT EXISTS _db_check (id INTEGER);")
                conn.execute("DROP TABLE IF EXISTS _db_check;")
            _db_module.DB_PATH = cand
            _db_module.DB_FOLDER = cand.parent
=======
            candidate.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(candidate))
            conn.execute("CREATE TABLE IF NOT EXISTS _db_check (id INTEGER);")
            conn.commit()
            conn.close()
          
            _db_module.DB_PATH = candidate
            _db_module.DB_FOLDER = candidate.parent
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

            def _safe_conn(_target=cand):
                _target.parent.mkdir(parents=True, exist_ok=True)
                c = sqlite3.connect(str(_target))
                for pragma in ("PRAGMA journal_mode=MEMORY;", "PRAGMA temp_store=MEMORY;", "PRAGMA synchronous=NORMAL;", "PRAGMA foreign_keys=ON;"):
                    try:
                        c.execute(pragma)
                    except sqlite3.Error:
                        pass
                return c

            _db_module.get_connection = _safe_conn
            return cand
        except Exception:
            continue

    fallback = Path(tempfile.gettempdir()) / "inventory.db"
    _db_module.DB_PATH = fallback
    _db_module.DB_FOLDER = fallback.parent
    return fallback


ACTIVE_DB_PATH = _ensure_writable_sqlite_path()

<<<<<<< HEAD

=======
# APPEARANCE

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# COLORS 

NAVY = "#172554"
NAVY_HOVER = "#243B78"
BLUE = "#2563EB"
BLUE_HOVER = "#1D4ED8"
GREEN = "#0F766E"
GREEN_HOVER = "#115E59"
RED = "#DC2626"
RED_HOVER = "#B91C1C"
ORANGE = "#D97706"
ORANGE_HOVER = "#B45309"
GRAY = "#64748B"
GRAY_HOVER = "#475569"
PAGE_BG = "#F4F6FA"
WHITE = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT = "#0F172A"
MUTED = "#64748B"


CHART_PALETTE = [
    "#2563EB",  # Primary Blue
    "#0F766E",  # Teal Green
    "#1E40AF",  # Deep Blue
    "#0D9488",  # Bright Teal
    "#3B82F6",  # Sky Blue
    "#D97706",  # Amber Orange
    "#64748B",  # Slate Muted 
]

# SIDEBAR BUTTON 

>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
class SidebarButton(ctk.CTkButton):
    _f_norm = None
    _f_bold = None

    def __init__(self, master, text, command=None):
        if SidebarButton._f_norm is None:
            SidebarButton._f_norm = ctk.CTkFont(size=14)
            SidebarButton._f_bold = ctk.CTkFont(size=14, weight="bold")
        super().__init__(
            master, text=text, command=command, anchor="w", height=42, corner_radius=7,
            fg_color="transparent", hover_color=NAVY_HOVER, text_color=WHITE, font=SidebarButton._f_norm
        )

    def set_active(self, active: bool):
        self.configure(fg_color=NAVY_HOVER if active else "transparent", font=SidebarButton._f_bold if active else SidebarButton._f_norm)

<<<<<<< HEAD
=======
# DASHBOARD APPLICATION
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
<<<<<<< HEAD
=======

       
        # STATE & PERFORMANCE CACHE FOR OLDER SYSTEMS
       
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        self.current_page = "Dashboard"
        self.inventory_tree = self.dashboard_tree = None
        self._search_after_id = self._pos_search_after_id = None
        self._active_figures = []
        self.cart_items = []
        self._pos_matched_products = []
        self._pos_selected_match_idx = 0
        self.report_top_n_var = None
        self.dashboard_status_filter = "All"
        self.inv_category_filter_var = self.inv_status_filter_var = self.inv_sort_var = None

<<<<<<< HEAD
        initialize_database()
        self._init_billing_and_settings_tables()
        self.app_settings = self._load_app_settings()

=======
        # DATABASE & PERSISTENT SETTINGS
       
        initialize_database()
        self._init_billing_and_settings_tables()
        self.app_settings = self._load_app_settings()
      
        # WINDOW
        
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        self.title(f"{self.app_settings['store_name']} - Inventory Management System")
        self.geometry("1400x830")
        self.minsize(1100, 650)
        self.configure(fg_color=PAGE_BG)

<<<<<<< HEAD
        self.f_title = ctk.CTkFont(size=30, weight="bold")
        self.f_sec = ctk.CTkFont(size=18, weight="bold")
        self.f_b14 = ctk.CTkFont(size=14, weight="bold")
        self.f_b12 = ctk.CTkFont(size=12, weight="bold")
        self.f_r13 = ctk.CTkFont(size=13)
        self.f_r12 = ctk.CTkFont(size=12)
        self.f_s11 = ctk.CTkFont(size=11)

=======
        self.font_page_title = ctk.CTkFont(size=30, weight="bold")
        self.font_section_title = ctk.CTkFont(size=18, weight="bold")
        self.font_card_title = ctk.CTkFont(size=12, weight="bold")
        self.font_card_value = ctk.CTkFont(size=24, weight="bold")
        self.font_bold_14 = ctk.CTkFont(size=14, weight="bold")
        self.font_bold_12 = ctk.CTkFont(size=12, weight="bold")
        self.font_regular_13 = ctk.CTkFont(size=13)
        self.font_regular_12 = ctk.CTkFont(size=12)
        self.font_small_11 = ctk.CTkFont(size=11)

        # Configure ttk Treeview
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        self._setup_treeview_styles()
        self._bind_shortcuts()

<<<<<<< HEAD
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.build_main_area()
        self.show_page("Dashboard")

    def _bind_shortcuts(self):
        bindings = {
            "<F1>": lambda _e: self.current_page == "Billing" and self._start_new_transaction(),
            "<F2>": lambda _e: self._shortcut_focus_scan_search(),
            "<F3>": lambda _e: self._shortcut_focus_invoice_history(),
            "<F4>": lambda _e: self._shortcut_focus_discount(),
            "<F8>": lambda _e: self.current_page == "Billing" and self._reprint_last_invoice(),
            "<F9>": lambda _e: self.current_page == "Billing" and self._show_pos_shortcuts_modal(),
            "<F10>": lambda _e: self.current_page == "Billing" and self._finalize_invoice(),
            "<Control-Return>": lambda _e: self.current_page == "Billing" and self._finalize_invoice(),
            "<Escape>": lambda _e: self._shortcut_escape(),
            "<Control-n>": lambda _e: self.current_page in ("Dashboard", "Inventory") and self.open_add_product(),
            "<Control-N>": lambda _e: self.current_page in ("Dashboard", "Inventory") and self.open_add_product(),
            "<Delete>": lambda _e: self.current_page == "Inventory" and self.inventory_tree and self.inventory_tree.winfo_exists() and self.inventory_tree.selection() and self.delete_selected_product(),
        }
        for key, fn in bindings.items():
            self.bind_all(key, fn)
=======
        # Bind global POS keyboard shortcuts 
        self._bind_pos_keyboard_shortcuts()

        # GRID
       
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # BUILD GUI
        
        self.build_sidebar()
        self.build_main_area()

        # START DASHBOARD
       
        self.show_page("Dashboard")

    # KEYBOARD SHORTCUTS FOR POS BILLING TERMINAL
    
    def _bind_pos_keyboard_shortcuts(self):
        self.bind_all("<F1>", self._shortcut_new_transaction)
        self.bind_all("<F2>", self._shortcut_focus_scan_search)
        self.bind_all("<F3>", self._shortcut_focus_invoice_history)
        self.bind_all("<F4>", self._shortcut_focus_discount)
        self.bind_all("<F8>", self._shortcut_reprint_last_receipt)
        self.bind_all("<F9>", self._shortcut_show_help)
        self.bind_all("<F10>", self._shortcut_checkout)
        self.bind_all("<Control-Return>", self._shortcut_checkout)
        self.bind_all("<Escape>", self._shortcut_escape)
        self.bind_all("<Control-n>", self._shortcut_add_product)
        self.bind_all("<Control-N>", self._shortcut_add_product)
        self.bind_all("<Delete>", self._shortcut_delete_selected_product)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

    def _shortcut_focus_scan_search(self):
        if self.current_page != "Billing":
            self.show_page("Billing")
        if hasattr(self, "pos_search_entry") and self.pos_search_entry.winfo_exists():
            self.pos_search_entry.focus_set()
            self.pos_search_entry.select_range(0, "end")

    def _shortcut_focus_invoice_history(self):
        if self.current_page == "Billing" and hasattr(self, "invoices_tree") and self.invoices_tree.winfo_exists():
            kids = self.invoices_tree.get_children()
            if kids:
                self.invoices_tree.focus_set()
                self.invoices_tree.selection_set(kids[0])
                self.invoices_tree.focus(kids[0])

    def _shortcut_focus_discount(self):
        if self.current_page == "Billing" and hasattr(self, "discount_entry") and self.discount_entry.winfo_exists():
            self.discount_entry.focus_set()
            self.discount_entry.select_range(0, "end")

    def _shortcut_escape(self):
        if self.current_page == "Billing" and hasattr(self, "pos_search_var") and self.pos_search_var.get().strip():
            self.pos_search_var.set("")
            self._update_pos_search_results()
            if hasattr(self, "pos_search_entry") and self.pos_search_entry.winfo_exists():
                self.pos_search_entry.focus_set()

<<<<<<< HEAD
=======
   
    # TREEVIEW STYLE INITIALIZATION 
    
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def _setup_treeview_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Inventory.Treeview", background=WHITE, fieldbackground=WHITE, foreground=TEXT, rowheight=32, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Inventory.Treeview.Heading", background=BORDER, foreground=TEXT, relief="flat", font=("Segoe UI", 10, "bold"))
        style.map("Inventory.Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", TEXT)])
        style.map("Inventory.Treeview.Heading", background=[("active", "#CBD5E1")])

<<<<<<< HEAD
    def _get_billing_db_path(self) -> Path:
=======
    # SQLITE STORAGE FOR BILLING & APP SETTINGS
   
    def _get_billing_db_path(self):
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        if hasattr(_db_module, "DB_PATH"):
            p = Path(getattr(_db_module, "DB_PATH"))
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                return p
            except Exception:
                pass
        return _ensure_writable_sqlite_path()

    def _db_conn(self) -> sqlite3.Connection:
        if hasattr(_db_module, "get_connection"):
            return _db_module.get_connection()
        return sqlite3.connect(str(self._get_billing_db_path()))

    def _init_billing_and_settings_tables(self):
        try:
            with self._db_conn() as conn:
                conn.executescript(
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
                    );
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
                    );
                    CREATE TABLE IF NOT EXISTS app_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                    """
                )
        except Exception:
            pass

    def _default_settings(self):
        return {
            "store_name": "IMABS",
            "store_tagline": "Inventory & Billing Management System",
            "store_address": "Varanasi, India",
            "store_contact": "+91 xxxxxxxx  |  GSTIN: xxxxxxxxxxxxxxx",
            "default_tax_pct": "18",
            "default_discount_pct": "0",
            "low_stock_threshold": "10",
            "currency_symbol": "Rs",
            "invoice_prefix": "INV",
        }

    def _load_app_settings(self):
        defaults = self._default_settings()
        try:
            with self._db_conn() as conn:
                for k, v in conn.execute("SELECT key, value FROM app_settings").fetchall():
                    if k in defaults and v is not None:
                        defaults[k] = str(v)
        except Exception:
            pass
        return defaults

    def _save_app_settings(self, new_settings: dict):
        with self._db_conn() as conn:
            for k, v in new_settings.items():
<<<<<<< HEAD
                conn.execute("INSERT INTO app_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (str(k), str(v)))
=======
                cur.execute(
                    """
                    INSERT INTO app_settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (str(k), str(v)),
                )
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
            try:
                thresh = max(1, int(float(new_settings.get("low_stock_threshold", 10))))
                conn.execute("UPDATE products SET status = CASE WHEN quantity <= 0 THEN 'Out of Stock' WHEN quantity <= ? THEN 'Low Stock' ELSE 'In Stock' END", (thresh,))
            except Exception:
                pass
            conn.commit()
        self.app_settings = self._load_app_settings()
        if hasattr(self, "sidebar_logo") and self.sidebar_logo.winfo_exists():
            self.sidebar_logo.configure(text=self.app_settings["store_name"][:12])
        self.title(f"{self.app_settings['store_name']} - Inventory Management System")

    def _get_sales_summary_stats(self):
        try:
            with self._db_conn() as conn:
                row = conn.execute("SELECT COUNT(*), COALESCE(SUM(grand_total), 0.0) FROM invoices").fetchone()
                if row:
                    return int(row[0] or 0), float(row[1] or 0.0)
        except Exception:
            pass
        return 0, 0.0

    def _generate_invoice_number(self):
        prefix = self.app_settings.get("invoice_prefix", "INV").strip() or "INV"
        now_str = datetime.now().strftime("%d%m%Y")
        count = 1
        try:
            with self._db_conn() as conn:
                row = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()
                if row and row[0] is not None:
                    count = int(row[0]) + 1
        except Exception:
            pass
        return f"{prefix}-{now_str}-{count:04d}"

    def _generate_next_sku(self):
        max_num = 1000
        for p in get_products():
            digits = "".join(ch for ch in str(p[1]) if ch.isdigit())
            if digits:
                try:
                    n = int(digits)
                    if 1 <= n <= 999999:
                        max_num = max(max_num, n)
                except ValueError:
                    pass
        return f"SKU-{max_num + 1}"

    def _fetch_recent_invoices(self, limit=50):
        try:
            with self._db_conn() as conn:
                return conn.execute(
                    """
                    SELECT i.id, i.invoice_no, i.created_at, i.customer_name, i.customer_phone,
                           i.payment_method, COUNT(ii.id), i.subtotal, i.discount_pct,
                           i.discount_amount, i.tax_pct, i.tax_amount, i.grand_total
                    FROM invoices i
                    LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
                    GROUP BY i.id ORDER BY i.id DESC LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        except Exception:
            return []

    def _fetch_invoice_items(self, invoice_id):
        try:
            with self._db_conn() as conn:
                return conn.execute(
                    "SELECT sku, product_name, quantity, unit_price, line_total FROM invoice_items WHERE invoice_id = ? ORDER BY id ASC",
                    (int(invoice_id),),
                ).fetchall()
        except Exception:
            return []

<<<<<<< HEAD
    def _build_receipt_data(self, row):
        items = [{"sku": r[0], "name": r[1], "qty": r[2], "price": float(r[3]), "total": float(r[4])} for r in self._fetch_invoice_items(int(row[0]))]
        return {
            "invoice_no": row[1],
            "created_at": _format_datetime_12h(row[2]),
            "customer_name": row[3],
            "customer_phone": row[4],
            "payment_method": row[5],
            "items": items,
            "breakdown": {
                "subtotal": float(row[7]), "disc_pct": float(row[8]), "disc_amount": float(row[9]),
                "tax_pct": float(row[10]), "tax_amount": float(row[11]), "grand_total": float(row[12]),
            },
        }

    def _card(self, parent, **kwargs):
        defaults = dict(fg_color=WHITE, corner_radius=10, border_width=1, border_color=BORDER)
        defaults.update(kwargs)
        return ctk.CTkFrame(parent, **defaults)

=======
    # SIDEBAR
   
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color=NAVY)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_propagate(False)
        self.sidebar_logo = ctk.CTkLabel(sidebar, text=self.app_settings.get("store_name", "IMABS")[:12], text_color=WHITE, font=ctk.CTkFont(size=25, weight="bold"))
        self.sidebar_logo.pack(pady=(35, 45))
        self.nav_buttons = {}
        for item in ("Dashboard", "Inventory", "Billing", "Reports", "Settings"):
            btn = SidebarButton(sidebar, text=item, command=lambda n=item: self.show_page(n))
            btn.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[item] = btn

<<<<<<< HEAD
=======
    # MAIN AREA
   
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def build_main_area(self):
        self.main = ctk.CTkFrame(self, fg_color=PAGE_BG, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nswe")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        topbar = ctk.CTkFrame(self.main, height=70, fg_color=WHITE, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="we")
        topbar.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(topbar, width=380, height=38, placeholder_text="Search inventory by SKU, name, or category...", textvariable=self.search_var, border_color="#94A3B8")
        self.search_entry.grid(row=0, column=0, padx=35, pady=16, sticky="w")
        self.search_entry.bind("<KeyRelease>", self._on_search_keyrelease)

        ctk.CTkButton(topbar, text="+ Create Invoice", width=140, height=38, fg_color=NAVY, hover_color=NAVY_HOVER, command=self.create_invoice).grid(row=0, column=1, padx=30)

        self.content = ctk.CTkScrollableFrame(self.main, fg_color=PAGE_BG, corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nswe", padx=35, pady=25)
        self.content.grid_columnconfigure(0, weight=1)

<<<<<<< HEAD
=======

    # MEMORY CLEANUP
    
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def clear_content(self):
        self.inventory_tree = self.dashboard_tree = None
        for fig in self._active_figures:
            try:
                fig.clear()
            except Exception:
                pass
        self._active_figures.clear()
        for w in self.content.winfo_children():
            w.destroy()

<<<<<<< HEAD
=======
        for widget in self.content.winfo_children():
            widget.destroy()

    # PAGE NAVIGATION

>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def show_page(self, page):
        self.current_page = page
        for name, btn in self.nav_buttons.items():
            btn.set_active(name == page)
        self.clear_content()
        {"Dashboard": self.show_dashboard, "Inventory": self.show_inventory, "Billing": self.show_billing, "Reports": self.show_reports, "Settings": self.show_settings}[page]()

<<<<<<< HEAD
    def show_dashboard(self):
        self.clear_content()
=======
        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Inventory":
            self.show_inventory()
        elif page == "Billing":
            self.show_billing()
        elif page == "Reports":
            self.show_reports()
        elif page == "Settings":
            self.show_settings()
   
    def show_dashboard(self):
        self.clear_content()
       
        # 1. HEADER WITH QUICK-ACTION TOOLBAR
        
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))
        t_col = ctk.CTkFrame(header, fg_color="transparent")
        t_col.pack(side="left")
        ctk.CTkLabel(t_col, text="Executive Overview", text_color=TEXT, font=self.f_title).pack(anchor="w")
        ctk.CTkLabel(t_col, text=f"{self.app_settings.get('store_name', 'IMABS')} — Real-time inventory, sales revenue & restock command center", text_color=MUTED, font=self.f_r13).pack(anchor="w", pady=(2, 0))

        qbar = ctk.CTkFrame(header, fg_color="transparent")
        qbar.pack(side="right", pady=4)
        for txt, w, fg, hv, cmd in (
            ("+ Add Product", 135, BLUE, BLUE_HOVER, self.open_add_product),
            ("🧾 New POS Invoice", 145, GREEN, GREEN_HOVER, self.create_invoice),
            ("📊 Analytics", 115, NAVY, NAVY_HOVER, lambda: self.show_page("Reports")),
            ("↻ Refresh", 95, GRAY, GRAY_HOVER, self.show_dashboard),
        ):
            ctk.CTkButton(qbar, text=txt, width=w, height=38, fg_color=fg, hover_color=hv, font=self.f_b12, command=cmd).pack(side="left", padx=(0, 8))

<<<<<<< HEAD
=======
        ctk.CTkLabel(
            title_col,
            text="Executive Overview",
            text_color=TEXT,
            font=self.font_page_title
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text=f"{self.app_settings.get('store_name', 'IMABS')} — Real-time inventory, sales revenue & restock command center",
            text_color=MUTED,
            font=self.font_regular_13
        ).pack(anchor="w", pady=(2, 0))

        quick_bar = ctk.CTkFrame(header, fg_color="transparent")
        quick_bar.pack(side="right", pady=4)

        ctk.CTkButton(
            quick_bar,
            text="+ Add Product",
            width=135,
            height=38,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=self.font_bold_12,
            command=self.open_add_product
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            quick_bar,
            text="🧾 New POS Invoice",
            width=145,
            height=38,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            font=self.font_bold_12,
            command=self.create_invoice
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            quick_bar,
            text="📊 Analytics",
            width=115,
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            font=self.font_bold_12,
            command=lambda: self.show_page("Reports")
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            quick_bar,
            text="↻ Refresh",
            width=95,
            height=38,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            font=self.font_bold_12,
            command=self.show_dashboard
        ).pack(side="left")
        
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        stats = get_dashboard_stats()
        all_products = get_products()
        total_units = sum(int(p[4]) for p in all_products)
        total_cats = len({str(p[3]) for p in all_products})
        inv_cnt, total_rev = self._get_sales_summary_stats()
        thresh = self.app_settings.get("low_stock_threshold", "10")

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 18))
        for i in range(5):
            cards.grid_columnconfigure(i, weight=1)
        for idx, args in enumerate((
            ("TOTAL STOCK VALUE", f"₹{stats.get('total_value', 0.0):,.2f}", f"{total_units:,} total units in stock", BLUE),
            ("TOTAL SALES REVENUE", f"₹{total_rev:,.2f}", f"Across {inv_cnt} completed invoices", GREEN),
            ("ACTIVE CATALOG", f"{stats.get('total_products', 0)} Products", f"Spanning {total_cats} categories", NAVY),
            ("LOW STOCK ALERTS", f"{stats.get('low_stock', 0)} Items", f"Stock ≤ {thresh} units threshold", ORANGE),
            ("OUT OF STOCK", f"{stats.get('out_of_stock', 0)} Items", "0 units — Immediate restock", RED),
        )):
            self.create_report_summary_card(cards, idx, *args)

        ws = ctk.CTkFrame(self.content, fg_color="transparent")
        ws.pack(fill="both", expand=True)
        ws.grid_columnconfigure(0, weight=7)
        ws.grid_columnconfigure(1, weight=3)

<<<<<<< HEAD
        left_panel = self._card(ws)
=======
        workspace = ctk.CTkFrame(self.content, fg_color="transparent")
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=7)
        workspace.grid_columnconfigure(1, weight=3)

        left_panel = ctk.CTkFrame(
            workspace,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ltop = ctk.CTkFrame(left_panel, fg_color="transparent")
        ltop.pack(fill="x", padx=22, pady=(18, 10))
        tstack = ctk.CTkFrame(ltop, fg_color="transparent")
        tstack.pack(side="left")
        ctk.CTkLabel(tstack, text="Live Inventory Explorer", text_color=TEXT, font=self.f_sec).pack(anchor="w")
        ctk.CTkLabel(tstack, text="Double-click any product row to edit details or adjust stock", text_color=MUTED, font=self.f_s11).pack(anchor="w", pady=(2, 0))

<<<<<<< HEAD
        fbar = ctk.CTkFrame(ltop, fg_color="transparent")
        fbar.pack(side="right")
        for opt in ("All", "In Stock", "Low Stock", "Out of Stock"):
            act = self.dashboard_status_filter == opt
=======
        left_top = ctk.CTkFrame(left_panel, fg_color="transparent")
        left_top.pack(fill="x", padx=22, pady=(18, 10))

        title_stack = ctk.CTkFrame(left_top, fg_color="transparent")
        title_stack.pack(side="left")

        ctk.CTkLabel(
            title_stack,
            text="Live Inventory Explorer",
            text_color=TEXT,
            font=self.font_section_title
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_stack,
            text="Double-click any product row to edit details or adjust stock",
            text_color=MUTED,
            font=self.font_small_11
        ).pack(anchor="w", pady=(2, 0))

        filter_bar = ctk.CTkFrame(left_top, fg_color="transparent")
        filter_bar.pack(side="right")

        for status_opt in ("All", "In Stock", "Low Stock", "Out of Stock"):
            is_active = (self.dashboard_status_filter == status_opt)
            pill_color = NAVY if is_active else PAGE_BG
            pill_text_color = WHITE if is_active else TEXT
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
            ctk.CTkButton(
                fbar, text=opt, width=84, height=30, corner_radius=6,
                fg_color=NAVY if act else PAGE_BG, hover_color=NAVY_HOVER if act else BORDER,
                text_color=WHITE if act else TEXT, font=self.f_b12 if act else self.f_r12,
                command=lambda s=opt: self._set_dashboard_status_filter(s),
            ).pack(side="left", padx=3)

        self.dashboard_tree = self.create_inventory_table(left_panel, self._get_filtered_dashboard_products(self.search_var.get().strip()), height=13)
        self.dashboard_tree.bind("<Double-1>", self._on_dashboard_tree_double_click)

<<<<<<< HEAD
        right_col = ctk.CTkFrame(ws, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        restock_card = self._card(right_col)
=======
        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        restock_card = ctk.CTkFrame(
            right_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        restock_card.pack(fill="both", expand=True, pady=(0, 12))
        rhead = ctk.CTkFrame(restock_card, fg_color="transparent")
        rhead.pack(fill="x", padx=18, pady=(16, 6))
        ctk.CTkLabel(rhead, text="⚡ Quick Restock Alerts", text_color=TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        alerts = sorted([p for p in all_products if int(p[4]) <= 0 or "low" in str(p[6]).lower() or "out" in str(p[6]).lower()], key=lambda x: int(x[4]))
        ctk.CTkLabel(rhead, text=f"{len(alerts)} Alerts", fg_color="#FEF3C7" if alerts else "#DCFCE7", text_color=ORANGE if alerts else GREEN, corner_radius=10, padx=10, pady=2, font=self.f_b12).pack(side="right")
        ctk.CTkLabel(restock_card, text="Click '+10' to instantly replenish low or out-of-stock items:", text_color=MUTED, font=self.f_s11).pack(anchor="w", padx=18, pady=(0, 6))

        rlist = ctk.CTkScrollableFrame(restock_card, fg_color=PAGE_BG, corner_radius=8, height=175)
        rlist.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        if not alerts:
            ctk.CTkLabel(rlist, text="✓ All products are well-stocked!", text_color=GREEN, font=self.f_b12).pack(pady=35)
        else:
            for prod in alerts[:12]:
                _, sku, name, _, qty, _, _ = prod
                rf = self._card(rlist, corner_radius=6)
                rf.pack(fill="x", padx=4, pady=3)
                inf = ctk.CTkFrame(rf, fg_color="transparent")
                inf.pack(side="left", fill="x", expand=True, padx=8, pady=5)
                ctk.CTkLabel(inf, text=name if len(str(name)) <= 22 else str(name)[:20] + "…", text_color=TEXT, font=self.f_b12, anchor="w").pack(anchor="w")
                ctk.CTkLabel(inf, text=f"{sku}  •  Stock: {qty}", text_color=RED if int(qty) <= 0 else ORANGE, font=self.f_s11, anchor="w").pack(anchor="w")
                ctk.CTkButton(rf, text="+10 Stock", width=74, height=26, corner_radius=5, fg_color=GREEN, hover_color=GREEN_HOVER, font=ctk.CTkFont(size=11, weight="bold"), command=lambda p=prod: self._quick_restock_product(p, 10)).pack(side="right", padx=8, pady=5)

<<<<<<< HEAD
        sales_card = self._card(right_col)
=======
                info_f = ctk.CTkFrame(row_f, fg_color="transparent")
                info_f.pack(side="left", fill="x", expand=True, padx=8, pady=5)

                ctk.CTkLabel(
                    info_f,
                    text=name if len(str(name)) <= 22 else str(name)[:20] + "…",
                    text_color=TEXT,
                    font=self.font_bold_12,
                    anchor="w"
                ).pack(anchor="w")

                ctk.CTkLabel(
                    info_f,
                    text=f"{sku}  •  Stock: {qty}",
                    text_color=RED if is_out else ORANGE,
                    font=self.font_small_11,
                    anchor="w"
                ).pack(anchor="w")

                ctk.CTkButton(
                    row_f,
                    text="+10 Stock",
                    width=74,
                    height=26,
                    corner_radius=5,
                    fg_color=GREEN,
                    hover_color=GREEN_HOVER,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda p=prod: self._quick_restock_product(p, 10)
                ).pack(side="right", padx=8, pady=5)

        sales_card = ctk.CTkFrame(
            right_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        sales_card.pack(fill="both", expand=True)
        shead = ctk.CTkFrame(sales_card, fg_color="transparent")
        shead.pack(fill="x", padx=18, pady=(14, 6))
        ctk.CTkLabel(shead, text="🧾 Recent Sales Activity", text_color=TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(shead, text="Open POS →", width=88, height=26, corner_radius=5, fg_color=NAVY, hover_color=NAVY_HOVER, font=ctk.CTkFont(size=11, weight="bold"), command=lambda: self.show_page("Billing")).pack(side="right")

        slist = ctk.CTkFrame(sales_card, fg_color=PAGE_BG, corner_radius=8)
        slist.pack(fill="both", expand=True, padx=16, pady=(4, 14))
        recent_invs = self._fetch_recent_invoices(limit=5)
        if not recent_invs:
            ctk.CTkLabel(slist, text="No invoices generated yet.\nClick '+ Create Invoice' to start billing.", text_color=MUTED, font=self.f_r12).pack(pady=30)
        else:
            for inv in recent_invs:
                ir = self._card(slist, corner_radius=6)
                ir.pack(fill="x", padx=6, pady=3)
                lc = ctk.CTkFrame(ir, fg_color="transparent")
                lc.pack(side="left", padx=8, pady=5)
                ctk.CTkLabel(lc, text=f"{inv[1]}  •  {inv[3]}", text_color=TEXT, font=self.f_b12).pack(anchor="w")
                ctk.CTkLabel(lc, text=f"{_format_datetime_12h(inv[2])}  |  {inv[5]} ({inv[6]} items)", text_color=MUTED, font=self.f_s11).pack(anchor="w")
                ctk.CTkLabel(ir, text=f"₹{float(inv[12]):,.2f}", text_color=GREEN, font=self.f_b12).pack(side="right", padx=10)

    def _set_dashboard_status_filter(self, choice):
        self.dashboard_status_filter = choice
        self.show_dashboard()

    def _get_filtered_dashboard_products(self, query=""):
        prods = search_products(query) if query else get_products()
        if self.dashboard_status_filter == "All":
            return prods
        t = self.dashboard_status_filter.lower()
        return [p for p in prods if str(p[6]).lower() == t]

    def _on_dashboard_tree_double_click(self, event=None):
        if not (self.dashboard_tree and self.dashboard_tree.winfo_exists()):
            return
        if event and not self.dashboard_tree.identify_row(event.y):
            return
        sel = self.dashboard_tree.selection()
        if sel:
            vals = self.dashboard_tree.item(sel[0], "values")
            if vals:
                self._open_product_form(vals)

    def _quick_restock_product(self, prod, add_qty=10):
        pid, sku, name, cat, qty, price, _ = prod
        ok, msg = update_product(int(pid), str(sku), str(name), str(cat), int(qty) + int(add_qty), float(price))
        if ok:
            self.show_dashboard() if self.current_page == "Dashboard" else self.refresh_inventory()
        else:
            messagebox.showerror("Restock Error", msg, parent=self)

<<<<<<< HEAD
    def show_inventory(self):
        self.clear_content()
=======
    # STAT CARD
   
    def create_stat_card(self, parent, column, title, value):
        card = ctk.CTkFrame(
            parent,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        card.grid(row=0, column=column, sticky="we", padx=6)

        label = ctk.CTkLabel(
            card,
            text=title,
            text_color=BLUE,
            font=self.font_card_title
        )
        label.pack(anchor="w", padx=20, pady=(20, 5))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            text_color=TEXT,
            font=self.font_card_value
        )
        value_label.pack(anchor="w", padx=20, pady=(0, 20))

    def show_inventory(self):
        self.clear_content()

>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        t_col = ctk.CTkFrame(header, fg_color="transparent")
        t_col.pack(side="left")
        ctk.CTkLabel(t_col, text="Inventory Management", text_color=TEXT, font=self.f_title).pack(anchor="w")
        ctk.CTkLabel(t_col, text="Filter, sort, adjust stock levels, or right-click any product row for quick actions", text_color=MUTED, font=self.f_r13).pack(anchor="w", pady=(2, 0))

        bbar = ctk.CTkFrame(header, fg_color="transparent")
        bbar.pack(side="right", pady=4)
        for txt, w, fg, hv, cmd, pad in (
            ("+ Add Product", 135, BLUE, BLUE_HOVER, self.open_add_product, (0, 0)),
            ("⚡ Adjust Stock", 125, NAVY, NAVY_HOVER, self.open_quick_stock_adjust, (0, 8)),
            ("📤 Export CSV", 120, GRAY, GRAY_HOVER, self.export_csv, (0, 8)),
            ("📥 Import CSV", 120, GREEN, GREEN_HOVER, self.import_csv, (0, 8)),
        ):
            ctk.CTkButton(bbar, text=txt, width=w, height=38, fg_color=fg, hover_color=hv, font=self.f_b12, command=cmd).pack(side="right", padx=pad)

<<<<<<< HEAD
        fcard = self._card(self.content)
        fcard.pack(fill="x", pady=(0, 14))
        frow = ctk.CTkFrame(fcard, fg_color="transparent")
        frow.pack(fill="x", padx=20, pady=12)
=======
        ctk.CTkLabel(
            title_col,
            text="Inventory Management",
            text_color=TEXT,
            font=self.font_page_title
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text="Filter, sort, adjust stock levels, or right-click any product row for quick actions",
            text_color=MUTED,
            font=self.font_regular_13
        ).pack(anchor="w", pady=(2, 0))

        button_bar = ctk.CTkFrame(header, fg_color="transparent")
        button_bar.pack(side="right", pady=4)

        ctk.CTkButton(
            button_bar,
            text="+ Add Product",
            width=135,
            height=38,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=self.font_bold_12,
            command=self.open_add_product
        ).pack(side="right")

        ctk.CTkButton(
            button_bar,
            text="⚡ Adjust Stock",
            width=125,
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            font=self.font_bold_12,
            command=self.open_quick_stock_adjust
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            button_bar,
            text="📤 Export CSV",
            width=120,
            height=38,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            font=self.font_bold_12,
            command=self.export_csv
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            button_bar,
            text="📥 Import CSV",
            width=120,
            height=38,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            font=self.font_bold_12,
            command=self.import_csv
        ).pack(side="right", padx=(0, 8))

        # FILTER, SORT & BULK CONTROL BAR CARD
        
        filter_card = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        filter_card.pack(fill="x", pady=(0, 14))

        f_row = ctk.CTkFrame(filter_card, fg_color="transparent")
        f_row.pack(fill="x", padx=20, pady=12)

        all_products = get_products()
        categories = sorted({str(p[3]) for p in all_products if p[3]})
        cat_options = ["All Categories"] + categories

        ctk.CTkLabel(
            f_row,
            text="Category:",
            text_color=TEXT,
            font=self.font_bold_12
        ).pack(side="left", padx=(0, 6))
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

        cats = ["All Categories"] + sorted({str(p[3]) for p in get_products() if p[3]})
        self.inv_category_filter_var = ctk.StringVar(value="All Categories")
        self.inv_status_filter_var = ctk.StringVar(value="All Statuses")
        self.inv_sort_var = ctk.StringVar(value="Newest First (ID ↓)")

        for lbl, var, vals, w, col, hov in (
            ("Category:", self.inv_category_filter_var, cats, 175, NAVY, NAVY_HOVER),
            ("Status:", self.inv_status_filter_var, ["All Statuses", "In Stock", "Low Stock", "Out of Stock"], 140, BLUE, BLUE_HOVER),
            ("Sort By:", self.inv_sort_var, ["Newest First (ID ↓)", "Product Name (A → Z)", "Quantity: Low to High", "Quantity: High to Low", "Unit Price: Low to High", "Unit Price: High to Low", "Stock Value: High to Low"], 185, NAVY, NAVY_HOVER),
        ):
            ctk.CTkLabel(frow, text=lbl, text_color=TEXT, font=self.f_b12).pack(side="left", padx=(0, 6))
            ctk.CTkOptionMenu(frow, variable=var, values=vals, width=w, height=34, fg_color=col, button_color=col, button_hover_color=hov, command=lambda _x: self.refresh_inventory()).pack(side="left", padx=(0, 12))

<<<<<<< HEAD
        ctk.CTkButton(frow, text="Reset Filters", width=100, height=34, fg_color=PAGE_BG, hover_color=BORDER, text_color=TEXT, border_width=1, border_color=BORDER, font=self.f_b12, command=self._reset_inventory_filters).pack(side="left")
        ctk.CTkButton(frow, text="🗑 Delete", width=85, height=34, fg_color=RED, hover_color=RED_HOVER, font=self.f_b12, command=self.delete_selected_product).pack(side="right")
        ctk.CTkButton(frow, text="✏ Edit Selected", width=115, height=34, fg_color=BLUE, hover_color=BLUE_HOVER, font=self.f_b12, command=self.edit_selected_product).pack(side="right", padx=(0, 8))

        self.inventory_panel = self._card(self.content)
=======
        ctk.CTkButton(
            f_row,
            text="🗑 Delete",
            width=85,
            height=34,
            fg_color=RED,
            hover_color=RED_HOVER,
            font=self.font_bold_12,
            command=self.delete_selected_product
        ).pack(side="right")

        ctk.CTkButton(
            f_row,
            text="✏ Edit Selected",
            width=115,
            height=34,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=self.font_bold_12,
            command=self.edit_selected_product
        ).pack(side="right", padx=(0, 8))

        self.inventory_panel = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        self.inventory_panel.pack(fill="both", expand=True)
        self.inv_summary_label = ctk.CTkLabel(self.content, text="", text_color=MUTED, font=self.f_b12)
        self.inv_summary_label.pack(anchor="w", pady=(8, 0))
        self.refresh_inventory()

    def _reset_inventory_filters(self):
        if self.inv_category_filter_var:
            self.inv_category_filter_var.set("All Categories")
        if self.inv_status_filter_var:
            self.inv_status_filter_var.set("All Statuses")
        if self.inv_sort_var:
            self.inv_sort_var.set("Newest First (ID ↓)")
        self.search_var.set("")
        self.refresh_inventory()

    def _get_filtered_and_sorted_inventory(self):
        q = self.search_var.get().strip()
        prods = list(search_products(q) if q else get_products())
        if self.inv_category_filter_var and (cf := self.inv_category_filter_var.get()) != "All Categories":
            prods = [p for p in prods if str(p[3]) == cf]
        if self.inv_status_filter_var and (sf := self.inv_status_filter_var.get()) != "All Statuses":
            prods = [p for p in prods if str(p[6]).lower() == sf.lower()]

        sort_map = {
            "Product Name (A → Z)": (lambda x: str(x[2]).lower(), False),
            "Quantity: Low to High": (lambda x: int(x[4]), False),
            "Quantity: High to Low": (lambda x: int(x[4]), True),
            "Unit Price: Low to High": (lambda x: float(x[5]), False),
            "Unit Price: High to Low": (lambda x: float(x[5]), True),
            "Stock Value: High to Low": (lambda x: int(x[4]) * float(x[5]), True),
        }
        key_fn, rev = sort_map.get(self.inv_sort_var.get() if self.inv_sort_var else "", (lambda x: int(x[0]), True))
        prods.sort(key=key_fn, reverse=rev)
        return prods

<<<<<<< HEAD
    def create_inventory_table(self, parent, products, height=13):
=======
        if self.inv_status_filter_var:
            st_filter = self.inv_status_filter_var.get()
            if st_filter and st_filter != "All Statuses":
                products = [p for p in products if str(p[6]).lower() == st_filter.lower()]

        sort_choice = self.inv_sort_var.get() if self.inv_sort_var else "Newest First (ID ↓)"
        if sort_choice == "Product Name (A → Z)":
            products.sort(key=lambda x: str(x[2]).lower())
        elif sort_choice == "Quantity: Low to High":
            products.sort(key=lambda x: int(x[4]))
        elif sort_choice == "Quantity: High to Low":
            products.sort(key=lambda x: int(x[4]), reverse=True)
        elif sort_choice == "Unit Price: Low to High":
            products.sort(key=lambda x: float(x[5]))
        elif sort_choice == "Unit Price: High to Low":
            products.sort(key=lambda x: float(x[5]), reverse=True)
        elif sort_choice == "Stock Value: High to Low":
            products.sort(key=lambda x: int(x[4]) * float(x[5]), reverse=True)
        else:
            products.sort(key=lambda x: int(x[0]), reverse=True)

        return products

    # INVENTORY TABLE 
  
    def create_inventory_table(self, parent, products, height=13, include_total_value=True):
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(14, 18))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "sku", "name", "category", "quantity", "price", "total_value", "status")
        meta = {
            "id": ("ID", 50), "sku": ("SKU", 105), "name": ("Product Name", 215), "category": ("Category", 145),
            "quantity": ("Quantity", 85), "price": ("Unit Price (₹)", 110), "total_value": ("Stock Value (₹)", 120), "status": ("Status", 110),
        }
        tree = ttk.Treeview(frame, columns=cols, show="headings", style="Inventory.Treeview", height=height)
        for col in cols:
            tree.heading(col, text=meta[col][0], command=lambda c=col, tr=tree: self._sort_treeview(tr, c, False))
            tree.column(col, width=meta[col][1], anchor="w")
        tree.tag_configure("low", foreground=ORANGE)
        tree.tag_configure("out", foreground=RED)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.grid(row=0, column=0, sticky="nswe")
        sb.grid(row=0, column=1, sticky="ns")
        self._populate_tree(tree, products)
        return tree

    def _sort_treeview(self, tree, col, reverse=False):
        if not (tree and tree.winfo_exists()):
            return
        def parse(v):
            c = str(v).replace("₹", "").replace(",", "").strip()
            try:
                return (0, float(c))
            except ValueError:
                return (1, c.lower())
        rows = sorted(((tree.set(k, col), k) for k in tree.get_children("")), key=lambda x: parse(x[0]), reverse=reverse)
        for idx, (_, k) in enumerate(rows):
            tree.move(k, "", idx)
        tree.heading(col, command=lambda c=col, tr=tree, rev=not reverse: self._sort_treeview(tr, c, rev))

    def _populate_tree(self, tree, products):
        if not (tree and tree.winfo_exists()):
            return
        tree.delete(*tree.get_children())
        for p in products:
            st = str(p[6]).lower() if len(p) > 6 else ""
            tag = ("out",) if "out" in st else (("low",) if "low" in st else ())
            qty, price = int(p[4]), float(p[5])
            tree.insert("", "end", values=(p[0], p[1], p[2], p[3], qty, f"{price:.2f}", f"{qty * price:,.2f}", p[6]), tags=tag)

<<<<<<< HEAD
=======
            qty_val = int(product[4])
            price_val = float(product[5])
            if include_total_value or len(tree["columns"]) == 8:
                formatted_row = (
                    product[0],
                    product[1],
                    product[2],
                    product[3],
                    qty_val,
                    f"{price_val:.2f}",
                    f"{qty_val * price_val:,.2f}",
                    product[6]
                )
            else:
                formatted_row = (
                    product[0],
                    product[1],
                    product[2],
                    product[3],
                    qty_val,
                    f"{price_val:.2f}",
                    product[6]
                )
            tree.insert("", "end", values=formatted_row, tags=tags)

    # REFRESH INVENTORY
    
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def refresh_inventory(self):
        if not (hasattr(self, "inventory_panel") and self.inventory_panel.winfo_exists()):
            return
        prods = self._get_filtered_and_sorted_inventory()
        if hasattr(self, "inv_summary_label") and self.inv_summary_label.winfo_exists():
            self.inv_summary_label.configure(
                text=f"Showing {len(prods)} products  •  Total Units: {sum(int(p[4]) for p in prods):,}  •  Filtered Stock Valuation: ₹{sum(int(p[4]) * float(p[5]) for p in prods):,.2f}"
            )
        if self.inventory_tree and self.inventory_tree.winfo_exists():
            self._populate_tree(self.inventory_tree, prods)
            return
        for w in self.inventory_panel.winfo_children():
            w.destroy()
        self.inventory_tree = self.create_inventory_table(self.inventory_panel, prods, height=13)
        self.inventory_tree.bind("<Double-1>", self.edit_selected_product)
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)

<<<<<<< HEAD
    def _on_search_keyrelease(self, _event=None):
=======
    # DEBOUNCED SEARCH 
    
    def _on_search_keyrelease(self, event=None):
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        if self._search_after_id is not None:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:
                pass
        self._search_after_id = self.after(180, self.search_inventory)

    def search_inventory(self):
        self._search_after_id = None
        if self.inventory_tree and self.inventory_tree.winfo_exists():
            self.refresh_inventory()
        elif self.dashboard_tree and self.dashboard_tree.winfo_exists():
            self._populate_tree(self.dashboard_tree, self._get_filtered_dashboard_products(self.search_var.get().strip()))

    def open_quick_stock_adjust(self):
        sel = self.inventory_tree.selection() if self.inventory_tree and self.inventory_tree.winfo_exists() else ()
        if not sel:
            messagebox.showinfo("Select a Product", "Please select a product row in the Inventory table first to adjust its stock.", parent=self)
            return
        vals = self.inventory_tree.item(sel[0], "values")
        pid, sku, name, cat, cur_qty, price = int(vals[0]), str(vals[1]), str(vals[2]), str(vals[3]), int(vals[4]), float(str(vals[5]).replace("₹", "").replace(",", ""))

        win = ctk.CTkToplevel(self)
        win.title(f"Quick Stock Adjust - {sku}")
        win.geometry("420x350")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="⚡ Quick Stock Adjustment", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT).pack(pady=(22, 6))
        ctk.CTkLabel(win, text=f"{name} ({sku})\nCurrent Stock: {cur_qty} units", text_color=MUTED, font=self.f_b12).pack(pady=(0, 16))
        pf = ctk.CTkFrame(win, fg_color="transparent")
        pf.pack(fill="x", padx=28, pady=(0, 14))

        def commit_qty(new_q):
            ok, msg = update_product(pid, sku, name, cat, new_q, price)
            if ok:
                win.destroy()
                self.refresh_inventory()
                self.refresh_dashboard_if_needed()
            else:
                messagebox.showerror("Error", msg, parent=win)

        for txt, delta, col in (("−5", -5, RED), ("−1", -1, ORANGE), ("+1", 1, BLUE), ("+5", 5, GREEN), ("+10", 10, GREEN), ("+25", 25, NAVY)):
            ctk.CTkButton(pf, text=txt, width=52, height=34, fg_color=col, command=lambda d=delta: commit_qty(max(0, cur_qty + d))).pack(side="left", expand=True, padx=2)

        ctk.CTkLabel(win, text="Or set exact new stock quantity:", text_color=TEXT, font=self.f_b12).pack(pady=(6, 4))
        exact = ctk.CTkEntry(win, height=36, justify="center")
        exact.pack(fill="x", padx=40, pady=(0, 16))
        exact.insert(0, str(cur_qty))

        def save_exact():
            try:
                q = int(exact.get().strip())
                if q < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Enter a non-negative integer.", parent=win)
                return
            commit_qty(q)

        ctk.CTkButton(win, text="Save Exact Stock", height=40, fg_color=BLUE, hover_color=BLUE_HOVER, command=save_exact).pack(fill="x", padx=40)

    def open_add_product(self):
        self._open_product_form(None)

    def edit_selected_product(self, event=None):
        if not (self.inventory_tree and self.inventory_tree.winfo_exists()):
            return
        if event and not self.inventory_tree.identify_row(event.y):
            return
        sel = self.inventory_tree.selection()
        if not sel:
            messagebox.showinfo("Select a Product", "Please select a product row first to edit.", parent=self)
            return
        vals = self.inventory_tree.item(sel[0], "values")
        if vals:
            self._open_product_form(vals)

    def _open_product_form(self, values=None):
        is_edit = values is not None
        win = ctk.CTkToplevel(self)
        win.title("Edit Product" if is_edit else "Add Product")
        win.geometry("460x560")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="Edit Product" if is_edit else "Add New Product", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT).pack(pady=(22, 16))
        fields = {}
        ctk.CTkLabel(win, text="SKU", anchor="w", text_color=TEXT).pack(fill="x", padx=40, pady=(6, 3))
        sku_row = ctk.CTkFrame(win, fg_color="transparent")
        sku_row.pack(fill="x", padx=40)
        sku_ent = ctk.CTkEntry(sku_row, height=38)
        sku_ent.pack(side="left", fill="x", expand=True, padx=(0, 8) if not is_edit else 0)
        sku_ent.insert(0, str(values[1]) if is_edit else self._generate_next_sku())
        fields["SKU"] = sku_ent
        if not is_edit:
            ctk.CTkButton(sku_row, text="Auto SKU", width=84, height=38, fg_color=NAVY, hover_color=NAVY_HOVER, font=self.f_b12, command=lambda: (sku_ent.delete(0, "end"), sku_ent.insert(0, self._generate_next_sku()))).pack(side="right")

        specs = [
            ("Product Name", "Product Name", str(values[2]) if is_edit else ""),
            ("Category", "Category", str(values[3]) if is_edit else ""),
            ("Quantity", "Quantity", str(values[4]) if is_edit else ""),
            ("Price", "Price" if is_edit else "Unit Price (₹ for 1 item)", str(values[5]).replace("₹", "").replace(",", "") if is_edit else ""),
        ]
        for key, lbl, init_val in specs:
            ctk.CTkLabel(win, text=lbl, anchor="w", text_color=TEXT).pack(fill="x", padx=40, pady=(8, 3))
            ent = ctk.CTkEntry(win, height=38)
            if init_val:
                ent.insert(0, init_val)
            ent.pack(fill="x", padx=40)
            fields[key] = ent

        def save():
            sku, name, cat = fields["SKU"].get().strip(), fields["Product Name"].get().strip(), fields["Category"].get().strip()
            qt, pt = fields["Quantity"].get().strip(), fields["Price"].get().strip().replace("₹", "").replace(",", "")
            if not all([sku, name, cat, qt, pt]):
                messagebox.showwarning("Missing Information", "Please fill all fields.", parent=win)
                return
            try:
                q, pr = int(qt), float(pt)
                if q < 0 or pr < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Data", "Quantity must be a non-negative integer and Price a non-negative number.", parent=win)
                return
            ok, msg = update_product(int(values[0]), sku, name, cat, q, pr) if is_edit else add_product(sku, name, cat, q, pr)
            if ok:
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                if is_edit:
                    self.refresh_inventory()
                    self.refresh_dashboard_if_needed()
                else:
                    self.show_inventory() if self.current_page == "Inventory" else self.refresh_dashboard_if_needed()
            else:
                messagebox.showerror("Error", msg, parent=win)

<<<<<<< HEAD
        ctk.CTkButton(win, text="Save Changes" if is_edit else "Add Product", height=42, fg_color=BLUE, hover_color=BLUE_HOVER, command=save).pack(fill="x", padx=40, pady=28)
=======
        ctk.CTkButton(
            win,
            text="Save Exact Stock",
            height=40,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=save_exact
        ).pack(fill="x", padx=40)
   
    # ADD PRODUCT WINDOW
   
    def open_add_product(self):
        window = ctk.CTkToplevel(self)
        window.title("Add Product")
        window.geometry("460x570")
        window.resizable(False, False)
        window.transient(self)
        window.grab_set()

        title = ctk.CTkLabel(
            window,
            text="Add New Product",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT
        )
        title.pack(pady=(22, 16))

        fields = {}
        sku_lbl_row = ctk.CTkFrame(window, fg_color="transparent")
        sku_lbl_row.pack(fill="x", padx=40, pady=(6, 3))
        ctk.CTkLabel(sku_lbl_row, text="SKU", anchor="w", text_color=TEXT).pack(side="left")

        sku_entry_row = ctk.CTkFrame(window, fg_color="transparent")
        sku_entry_row.pack(fill="x", padx=40)
        sku_entry = ctk.CTkEntry(sku_entry_row, height=38)
        sku_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        sku_entry.insert(0, self._generate_next_sku())
        fields["SKU"] = sku_entry

        ctk.CTkButton(
            sku_entry_row,
            text="Auto SKU",
            width=84,
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            font=self.font_bold_12,
            command=lambda: (
                sku_entry.delete(0, "end"),
                sku_entry.insert(0, self._generate_next_sku())
            )
        ).pack(side="right")

        for field in ["Product Name", "Category", "Quantity", "Price"]:
            label = ctk.CTkLabel(
                window,
                text=field if field != "Price" else "Unit Price (₹ for 1 item)",
                anchor="w",
                text_color=TEXT
            )
            label.pack(fill="x", padx=40, pady=(8, 3))

            entry = ctk.CTkEntry(window, height=38)
            entry.pack(fill="x", padx=40)
            fields[field] = entry

        def save_product():
            sku = fields["SKU"].get().strip()
            name = fields["Product Name"].get().strip()
            category = fields["Category"].get().strip()
            quantity_text = fields["Quantity"].get().strip()
            price_text = fields["Price"].get().strip().replace("₹", "").replace(",", "")

            if not all([sku, name, category, quantity_text, price_text]):
                messagebox.showwarning(
                    "Missing Information",
                    "Please fill all fields.",
                    parent=window
                )
                return

            try:
                quantity = int(quantity_text)
                price = float(price_text)
            except ValueError:
                messagebox.showerror(
                    "Invalid Data",
                    "Quantity must be a whole number and Price must be a number.",
                    parent=window
                )
                return

            if quantity < 0 or price < 0:
                messagebox.showerror(
                    "Invalid Data",
                    "Quantity and Price cannot be negative.",
                    parent=window
                )
                return

            success, message = add_product(
                sku,
                name,
                category,
                quantity,
                price
            )
            if success:
                messagebox.showinfo("Success", message, parent=window)
                window.destroy()
                if self.current_page == "Inventory":
                    self.show_inventory()
                else:
                    self.refresh_dashboard_if_needed()
            else:
                messagebox.showerror("Error", message, parent=window)

        save_button = ctk.CTkButton(
            window,
            text="Add Product",
            height=42,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=save_product
        )
        save_button.pack(fill="x", padx=40, pady=28)

    # EDIT PRODUCT 
    
    def edit_selected_product(self, event=None):
        if self.inventory_tree is None or not self.inventory_tree.winfo_exists():
            return

        if event is not None:
            clicked_row = self.inventory_tree.identify_row(event.y)
            if not clicked_row:
                return

        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Select a Product",
                "Please select a product row first to edit.",
                parent=self
            )
            return

        values = self.inventory_tree.item(selected[0], "values")
        if values:
            self.open_edit_product(values)

    # EDIT WINDOW
   
    def open_edit_product(self, values):
        window = ctk.CTkToplevel(self)
        window.title("Edit Product")
        window.geometry("450x550")
        window.resizable(False, False)
        window.transient(self)
        window.grab_set()

        title = ctk.CTkLabel(
            window,
            text="Edit Product",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT
        )
        title.pack(pady=(25, 20))

        fields = {}
        field_names = [
            "SKU",
            "Product Name",
            "Category",
            "Quantity",
            "Price"
        ]
        current_values = [
            values[1],
            values[2],
            values[3],
            values[4],
            str(values[5]).replace("₹", "").replace(",", "")
        ]
        for field, current in zip(field_names, current_values):
            label = ctk.CTkLabel(
                window,
                text=field,
                anchor="w",
                text_color=TEXT
            )
            label.pack(fill="x", padx=40, pady=(8, 3))

            entry = ctk.CTkEntry(window, height=38)
            entry.insert(0, str(current))
            entry.pack(fill="x", padx=40)
            fields[field] = entry

        def save_changes():
            sku = fields["SKU"].get().strip()
            name = fields["Product Name"].get().strip()
            category = fields["Category"].get().strip()
            quantity_text = fields["Quantity"].get().strip()
            price_text = fields["Price"].get().strip().replace("₹", "").replace(",", "")

            if not all([sku, name, category, quantity_text, price_text]):
                messagebox.showwarning(
                    "Missing Information",
                    "Please fill all fields.",
                    parent=window
                )
                return

            try:
                quantity = int(quantity_text)
                price = float(price_text)
            except ValueError:
                messagebox.showerror(
                    "Invalid Data",
                    "Quantity must be an integer and Price must be a number.",
                    parent=window
                )
                return

            if quantity < 0 or price < 0:
                messagebox.showerror(
                    "Invalid Data",
                    "Quantity and Price cannot be negative.",
                    parent=window
                )
                return

            success, message = update_product(
                int(values[0]),
                sku,
                name,
                category,
                quantity,
                price
            )
            if success:
                messagebox.showinfo("Success", message, parent=window)
                window.destroy()
                self.refresh_inventory()
                self.refresh_dashboard_if_needed()
            else:
                messagebox.showerror("Error", message, parent=window)

        save_button = ctk.CTkButton(
            window,
            text="Save Changes",
            height=42,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=save_changes
        )
        save_button.pack(fill="x", padx=40, pady=30)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

    def show_context_menu(self, event):
        if not (self.inventory_tree and self.inventory_tree.winfo_exists()):
            return
        item = self.inventory_tree.identify_row(event.y)
        if not item:
            return
        self.inventory_tree.selection_set(item)
        vals = self.inventory_tree.item(item, "values")
        menu = tk.Menu(self, tearoff=0, bg=WHITE, fg=TEXT, activebackground=BLUE, activeforeground=WHITE, font=("Segoe UI", 10))
        menu.add_command(label="✏  Edit Product", command=self.edit_selected_product)
        menu.add_command(label="⚡  Quick Stock Adjust...", command=self.open_quick_stock_adjust)
        if vals:
            pt = (int(vals[0]), str(vals[1]), str(vals[2]), str(vals[3]), int(vals[4]), float(str(vals[5]).replace("₹", "").replace(",", "")), str(vals[-1]))
            menu.add_command(label="➕  Quick Restock (+10 Units)", command=lambda p=pt: self._quick_restock_product(p, 10))
            menu.add_command(label="🛒  Send to Billing Cart", command=lambda p=pt: self._send_product_tuple_to_pos_cart(p))
        menu.add_separator()
        menu.add_command(label="🗑  Delete Product", foreground=RED, command=self.delete_selected_product)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _send_product_tuple_to_pos_cart(self, pt):
        pid, sku, name, cat, qty, price, status = pt
        if qty <= 0:
            messagebox.showwarning("Out of Stock", f"'{name}' is Out of Stock. Restock it first before billing.", parent=self)
            return
        self._add_product_dict_to_cart({"id": pid, "sku": sku, "name": name, "category": cat, "stock": qty, "price": price, "status": status})
        messagebox.showinfo("Added to POS Cart", f"1 unit of '{name}' ({sku}) was added to the Billing Cart.", parent=self)

<<<<<<< HEAD
=======
    # DELETE PRODUCT
   
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def delete_selected_product(self):
        if not (self.inventory_tree and self.inventory_tree.winfo_exists()):
            return
        sel = self.inventory_tree.selection()
        if not sel:
            messagebox.showinfo("Select a Product", "Please select a product row first to delete.", parent=self)
            return
        vals = self.inventory_tree.item(sel[0], "values")
        if not messagebox.askyesno("Delete Product", f"Are you sure you want to delete:\n\n{vals[2]}?", parent=self):
            return
        ok, msg = delete_product(int(vals[0]))
        if ok:
            messagebox.showinfo("Deleted", msg)
            self.refresh_inventory()
            self.refresh_dashboard_if_needed()
        else:
            messagebox.showerror("Error", msg)

<<<<<<< HEAD
=======
    # IMPORT CSV
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def import_csv(self):
        path = filedialog.askopenfilename(title="Select Inventory CSV", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not path:
            return
        try:
            added, skipped, errs = import_products_from_csv(path)
            self.show_inventory() if self.current_page == "Inventory" else self.refresh_dashboard_if_needed()
            if skipped == 0:
                messagebox.showinfo("Import Complete", f"{added} products imported successfully.")
            else:
                et = "\n".join(errs[:10]) + ("\n\n...and more errors." if len(errs) > 10 else "")
                messagebox.showwarning("Import Completed", f"Products added: {added}\nProducts skipped: {skipped}\n\n{et}")
        except Exception as err:
            messagebox.showerror("Import Error", f"Could not import CSV file.\n\n{err}")

<<<<<<< HEAD
=======
    # EXPORT CSV
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def export_csv(self):
        path = filedialog.asksaveasfilename(title="Export Inventory", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="inventory_export.csv")
        if not path:
            return
        try:
            messagebox.showinfo("Export Complete", f"{export_products_to_csv(path)} products exported successfully.\n\nSaved to:\n{path}")
        except Exception as err:
            messagebox.showerror("Export Error", f"Could not export CSV.\n\n{err}")

    def refresh_dashboard_if_needed(self):
        if self.current_page == "Dashboard":
            self.show_dashboard()

    def show_billing(self):
        self._billing_products = [{"id": int(p[0]), "sku": str(p[1]), "name": str(p[2]), "category": str(p[3]), "stock": int(p[4]), "price": float(p[5]), "status": str(p[6])} for p in get_products()]

<<<<<<< HEAD
        ph = self._card(self.content)
        ph.pack(fill="x", pady=(0, 14))
        tbar = ctk.CTkFrame(ph, fg_color="transparent")
        tbar.pack(fill="x", padx=22, pady=(16, 10))
=======
       
        pos_header_card = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        pos_header_card.pack(fill="x", pady=(0, 14))
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

        bcol = ctk.CTkFrame(tbar, fg_color="transparent")
        bcol.pack(side="left")
        tline = ctk.CTkFrame(bcol, fg_color="transparent")
        tline.pack(anchor="w")
        ctk.CTkLabel(tline, text=f"🧾 {self.app_settings.get('store_name', 'IMABS')} POS Terminal", font=ctk.CTkFont(size=22, weight="bold"), text_color=BLUE).pack(side="left")
        ctk.CTkLabel(tline, text="   ● Status: Online", font=self.f_b12, text_color=GREEN).pack(side="left", pady=(3, 0))

        self.invoice_no_var = ctk.StringVar(value=self._generate_invoice_number())
        mline = ctk.CTkFrame(bcol, fg_color="transparent")
        mline.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(mline, text="TXN: #", text_color=MUTED, font=self.f_b12).pack(side="left")
        ctk.CTkLabel(mline, textvariable=self.invoice_no_var, text_color=TEXT, font=self.f_b12).pack(side="left")
        ctk.CTkLabel(mline, text="   |   Shortcuts: F1 New  •  F2 Scan/Search  •  F4 Discount  •  F8 Reprint  •  F10 Checkout", text_color=MUTED, font=self.f_s11).pack(side="left")

        abtns = ctk.CTkFrame(tbar, fg_color="transparent")
        abtns.pack(side="right")
        for txt, w, fg, hv, cmd in (
            ("⊕ New Transaction  [F1]", 165, GREEN, GREEN_HOVER, self._start_new_transaction),
            ("🔍 Product Search  [F2]", 160, BLUE, BLUE_HOVER, self._shortcut_focus_scan_search),
            ("📤 Export Invoices", 135, ORANGE, ORANGE_HOVER, self._export_invoices_csv),
            ("🗑 Clear Cart", 105, GRAY, GRAY_HOVER, self._clear_cart),
        ):
            ctk.CTkButton(abtns, text=txt, height=36, width=w, corner_radius=7, fg_color=fg, hover_color=hv, font=self.f_b12, command=cmd).pack(side="left", padx=(0, 8))

        cstrip = ctk.CTkFrame(ph, fg_color=PAGE_BG, corner_radius=8)
        cstrip.pack(fill="x", padx=22, pady=(2, 14))
        for col_i, wt in ((1, 2), (3, 2), (5, 1)):
            cstrip.grid_columnconfigure(col_i, weight=wt)

        ctk.CTkLabel(cstrip, text="Customer:", text_color=TEXT, font=self.f_b12).grid(row=0, column=0, padx=(14, 6), pady=8, sticky="w")
        self.cust_name_entry = ctk.CTkEntry(cstrip, height=32, placeholder_text="Walk-in Customer / Enter Name", border_color=BORDER, fg_color=WHITE)
        self.cust_name_entry.grid(row=0, column=1, padx=(0, 14), pady=8, sticky="we")
        ctk.CTkLabel(cstrip, text="Phone:", text_color=TEXT, font=self.f_b12).grid(row=0, column=2, padx=(4, 6), pady=8, sticky="w")
        self.cust_phone_entry = ctk.CTkEntry(cstrip, height=32, placeholder_text="+91 9876543210 (Optional)", border_color=BORDER, fg_color=WHITE)
        self.cust_phone_entry.grid(row=0, column=3, padx=(0, 14), pady=8, sticky="we")
        ctk.CTkLabel(cstrip, text="Payment Mode:", text_color=TEXT, font=self.f_b12).grid(row=0, column=4, padx=(4, 6), pady=8, sticky="w")
        self.payment_method_var = ctk.StringVar(value="Cash")
        ctk.CTkOptionMenu(cstrip, variable=self.payment_method_var, values=["Cash", "UPI", "Card", "Bank Transfer"], height=32, fg_color=NAVY, button_color=NAVY, button_hover_color=NAVY_HOVER).grid(row=0, column=5, padx=(0, 14), pady=8, sticky="we")

<<<<<<< HEAD
        ws = ctk.CTkFrame(self.content, fg_color="transparent")
        ws.pack(fill="both", expand=True)
        ws.grid_columnconfigure(0, weight=7)
        ws.grid_columnconfigure(1, weight=3)
=======
        workspace = ctk.CTkFrame(self.content, fg_color="transparent")
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=7)
        workspace.grid_columnconfigure(1, weight=3)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

        lcol = ctk.CTkFrame(ws, fg_color="transparent")
        lcol.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        scard = self._card(lcol)
        scard.pack(fill="x", pady=(0, 14))
        strow = ctk.CTkFrame(scard, fg_color="transparent")
        strow.pack(fill="x", padx=20, pady=(14, 6))
        ctk.CTkLabel(strow, text="🔍 Scan Products / Quick Search", font=self.f_b14, text_color=TEXT).pack(side="left")
        ctk.CTkLabel(strow, text="Type SKU or Product Name  •  ↑/↓ Select  •  Press Enter ↵ to Add to Cart", font=self.f_s11, text_color=MUTED).pack(side="right")

        sbar = ctk.CTkFrame(scard, fg_color=WHITE, corner_radius=8, border_width=2, border_color=BLUE)
        sbar.pack(fill="x", padx=20, pady=(0, 10))
        sbar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(sbar, text="🏷", font=ctk.CTkFont(size=16), text_color=BLUE).grid(row=0, column=0, padx=(12, 4), pady=6)
        self.pos_search_var = ctk.StringVar()
        self.pos_search_entry = ctk.CTkEntry(sbar, textvariable=self.pos_search_var, height=36, border_width=0, fg_color=WHITE, text_color=TEXT, font=self.f_r13, placeholder_text="Scan barcode, SKU, or enter product name... (e.g. SKU-1001, Mouse, Monitor)")
        self.pos_search_entry.grid(row=0, column=1, sticky="we", padx=4, pady=4)
        ctk.CTkLabel(sbar, text="Qty:", font=self.f_b12, text_color=MUTED).grid(row=0, column=2, padx=(6, 4), pady=4)
        self.bill_qty_entry = ctk.CTkEntry(sbar, width=52, height=30, border_width=1, border_color=BORDER, fg_color=PAGE_BG, justify="center", font=self.f_b12)
        self.bill_qty_entry.insert(0, "1")
        self.bill_qty_entry.grid(row=0, column=3, padx=(0, 8), pady=4)
        ctk.CTkButton(sbar, text="Enter ↵", width=76, height=30, corner_radius=6, fg_color=PAGE_BG, hover_color=BLUE, text_color=TEXT, border_width=1, border_color=BORDER, font=self.f_b12, command=self._on_pos_search_enter).grid(row=0, column=4, padx=(0, 8), pady=4)

        self.pos_search_entry.bind("<KeyRelease>", self._on_pos_search_keyrelease)
        self.pos_search_entry.bind("<Return>", self._on_pos_search_enter)
        self.pos_search_entry.bind("<Down>", lambda _e: self._move_pos_sel(1))
        self.pos_search_entry.bind("<Up>", lambda _e: self._move_pos_sel(-1))
        self.bill_qty_entry.bind("<Return>", self._on_pos_search_enter)

        self.pos_suggestions_frame = ctk.CTkFrame(scard, fg_color=PAGE_BG, corner_radius=8)
        self.pos_suggestions_frame.pack(fill="x", padx=20, pady=(0, 14))

        ccard = self._card(lcol)
        ccard.pack(fill="both", expand=True)
        ctop = ctk.CTkFrame(ccard, fg_color="transparent")
        ctop.pack(fill="x", padx=20, pady=(16, 10))
        ctk.CTkLabel(ctop, text="🛒 Shopping Cart", font=self.f_sec, text_color=TEXT).pack(side="left")
        self.cart_badge_label = ctk.CTkLabel(ctop, text="0 Items", fg_color="#DBEAFE", text_color=BLUE, corner_radius=12, padx=12, pady=3, font=self.f_b12)
        self.cart_badge_label.pack(side="right")

        chdr = ctk.CTkFrame(ccard, fg_color=PAGE_BG, corner_radius=6, height=34)
        chdr.pack(fill="x", padx=20, pady=(0, 6))
        self._cfg_cart_cols(chdr)
        for ci, txt, al in ((0, "PRODUCT DETAILS", "w"), (1, "PRICE", "e"), (2, "QTY", "center"), (3, "DISC.", "e"), (4, "TAX", "e"), (5, "TOTAL", "e"), (6, "ACTION", "center")):
            ctk.CTkLabel(chdr, text=txt, font=ctk.CTkFont(size=11, weight="bold"), text_color=MUTED, anchor=al).grid(row=0, column=ci, sticky="we", padx=8, pady=6)

        self.cart_rows_container = ctk.CTkScrollableFrame(ccard, fg_color=WHITE, corner_radius=0, height=290)
        self.cart_rows_container.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.cart_rows_container.grid_columnconfigure(0, weight=1)

<<<<<<< HEAD
        rcol = ctk.CTkFrame(ws, fg_color="transparent")
        rcol.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        sum_card = ctk.CTkFrame(rcol, fg_color=NAVY, corner_radius=12, border_width=1, border_color=NAVY_HOVER)
        sum_card.pack(fill="both", expand=True)
        ctk.CTkLabel(sum_card, text="🧾 Cart Summary", font=ctk.CTkFont(size=19, weight="bold"), text_color=WHITE).pack(anchor="w", padx=22, pady=(20, 12))
=======
        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

        tdbox = ctk.CTkFrame(sum_card, fg_color=NAVY_HOVER, corner_radius=8)
        tdbox.pack(fill="x", padx=22, pady=(0, 14))
        tdbox.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(tdbox, text="Discount (%)  [F4]", text_color="#CBD5E1", font=self.f_b12, anchor="w").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 3))
        ctk.CTkLabel(tdbox, text="Tax / GST (%)", text_color="#CBD5E1", font=self.f_b12, anchor="w").grid(row=0, column=1, sticky="w", padx=(6, 12), pady=(10, 3))

        self.discount_var = ctk.StringVar(value=self.app_settings.get("default_discount_pct", "0"))
        self.discount_entry = ctk.CTkEntry(tdbox, height=32, textvariable=self.discount_var, fg_color=WHITE, text_color=TEXT, border_color=BORDER)
        self.discount_entry.grid(row=1, column=0, sticky="we", padx=(12, 6), pady=(0, 10))
        self.discount_entry.bind("<KeyRelease>", lambda _e: self._refresh_cart_table())

        self.tax_var = ctk.StringVar(value=self.app_settings.get("default_tax_pct", "18"))
        self.tax_entry = ctk.CTkEntry(tdbox, height=32, textvariable=self.tax_var, fg_color=WHITE, text_color=TEXT, border_color=BORDER)
        self.tax_entry.grid(row=1, column=1, sticky="we", padx=(6, 12), pady=(0, 10))
        self.tax_entry.bind("<KeyRelease>", lambda _e: self._refresh_cart_table())

        mf = ctk.CTkFrame(sum_card, fg_color="transparent")
        mf.pack(fill="x", padx=22, pady=(2, 8))
        self.lbl_items_count = self._pos_sum_row(mf, "Items Count:", "0 items (0 qty)", WHITE)
        self.lbl_subtotal = self._pos_sum_row(mf, "Subtotal:", "₹0.00", WHITE)
        self.lbl_discount = self._pos_sum_row(mf, "Total Discount:", "-₹0.00", "#FBBF24")
        self.lbl_tax = self._pos_sum_row(mf, "Tax (GST):", "+₹0.00", "#34D399")
        ctk.CTkFrame(sum_card, height=1, fg_color=NAVY_HOVER).pack(fill="x", padx=22, pady=10)

        grow = ctk.CTkFrame(sum_card, fg_color="transparent")
        grow.pack(fill="x", padx=22, pady=(2, 16))
        ctk.CTkLabel(grow, text="Total\nAmount:", justify="left", font=ctk.CTkFont(size=15, weight="bold"), text_color="#CBD5E1").pack(side="left")
        self.lbl_grand_total = ctk.CTkLabel(grow, text="₹0.00", font=ctk.CTkFont(size=28, weight="bold"), text_color=WHITE)
        self.lbl_grand_total.pack(side="right")

        bstack = ctk.CTkFrame(sum_card, fg_color="transparent")
        bstack.pack(fill="x", padx=22, pady=(4, 10))
        self.checkout_btn = ctk.CTkButton(bstack, text="🛍  Checkout (₹0.00)  [F10]", height=46, corner_radius=8, fg_color=GREEN, hover_color=GREEN_HOVER, font=ctk.CTkFont(size=15, weight="bold"), command=self._finalize_invoice)
        self.checkout_btn.pack(fill="x", pady=(0, 8))
        for txt, h, fg, hv, cmd in (
            ("🏷  Quick Discount / Coupon  [F4]", 38, ORANGE, ORANGE_HOVER, self._open_quick_discount_dialog),
            ("🖨  Reprint Last Receipt  [F8]", 38, BLUE, BLUE_HOVER, self._reprint_last_invoice),
            ("⌨  Help & Keyboard Shortcuts  [F9]", 36, NAVY_HOVER, GRAY_HOVER, self._show_pos_shortcuts_modal),
        ):
            ctk.CTkButton(bstack, text=txt, height=h, corner_radius=8, fg_color=fg, hover_color=hv, font=self.f_b12, command=cmd).pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(sum_card, text="Press F10 to complete sale  •  Press F2 to scan", text_color="#94A3B8", font=self.f_s11).pack(pady=(2, 14))

        hcard = self._card(self.content)
        hcard.pack(fill="both", expand=True, pady=(16, 0))
        ctk.CTkLabel(hcard, text="Recent Invoices  [F3]  (Double-click an invoice to view or save receipt)", font=self.f_sec, text_color=TEXT).pack(anchor="w", padx=20, pady=(14, 8))

<<<<<<< HEAD
        hf = ctk.CTkFrame(hcard, fg_color="transparent")
        hf.pack(fill="both", expand=True, padx=20, pady=(2, 16))
        hf.grid_columnconfigure(0, weight=1)
        hf.grid_rowconfigure(0, weight=1)
        icols = (("id", "ID", 45), ("invoice_no", "Invoice #", 145), ("date", "Date & Time", 170), ("customer", "Customer Name", 165), ("phone", "Phone", 115), ("payment", "Payment", 95), ("items", "Items", 60), ("total", "Grand Total (₹)", 120))
        self.invoices_tree = ttk.Treeview(hf, columns=[c[0] for c in icols], show="headings", style="Inventory.Treeview", height=5)
        for cid, head, w in icols:
            self.invoices_tree.heading(cid, text=head)
            self.invoices_tree.column(cid, width=w, anchor="w")
        isb = ttk.Scrollbar(hf, orient="vertical", command=self.invoices_tree.yview)
        self.invoices_tree.configure(yscrollcommand=isb.set)
=======
        ctk.CTkButton(
            btn_stack,
            text="🖨  Reprint Last Receipt  [F8]",
            height=38,
            corner_radius=8,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=self.font_bold_12,
            command=self._reprint_last_invoice
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_stack,
            text="⌨  Help & Keyboard Shortcuts  [F9]",
            height=36,
            corner_radius=8,
            fg_color=NAVY_HOVER,
            hover_color=GRAY_HOVER,
            font=self.font_bold_12,
            command=self._show_pos_shortcuts_modal
        ).pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            summary_card,
            text="Press F10 to complete sale  •  Press F2 to scan",
            text_color="#94A3B8",
            font=self.font_small_11
        ).pack(pady=(2, 14))

        history_card = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        history_card.pack(fill="both", expand=True, pady=(16, 0))

        hist_header = ctk.CTkFrame(history_card, fg_color="transparent")
        hist_header.pack(fill="x", padx=20, pady=(14, 8))

        ctk.CTkLabel(
            hist_header,
            text="Recent Invoices  [F3]  (Double-click an invoice to view or save receipt)",
            font=self.font_section_title,
            text_color=TEXT
        ).pack(side="left")

        hist_table_frame = ctk.CTkFrame(history_card, fg_color="transparent")
        hist_table_frame.pack(fill="both", expand=True, padx=20, pady=(2, 16))
        hist_table_frame.grid_columnconfigure(0, weight=1)
        hist_table_frame.grid_rowconfigure(0, weight=1)

        inv_cols = ("id", "invoice_no", "date", "customer", "phone", "payment", "items", "total")
        self.invoices_tree = ttk.Treeview(
            hist_table_frame,
            columns=inv_cols,
            show="headings",
            style="Inventory.Treeview",
            height=5
        )
        inv_headings = {
            "id": "ID",
            "invoice_no": "Invoice #",
            "date": "Date & Time",
            "customer": "Customer Name",
            "phone": "Phone",
            "payment": "Payment",
            "items": "Items",
            "total": "Grand Total (₹)"
        }
        inv_widths = {
            "id": 45,
            "invoice_no": 140,
            "date": 145,
            "customer": 170,
            "phone": 115,
            "payment": 100,
            "items": 65,
            "total": 120
        }
        for col in inv_cols:
            self.invoices_tree.heading(col, text=inv_headings[col])
            self.invoices_tree.column(col, width=inv_widths[col], anchor="w")

        inv_scroll = ttk.Scrollbar(
            hist_table_frame,
            orient="vertical",
            command=self.invoices_tree.yview
        )
        self.invoices_tree.configure(yscrollcommand=inv_scroll.set)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        self.invoices_tree.grid(row=0, column=0, sticky="nswe")
        isb.grid(row=0, column=1, sticky="ns")
        self.invoices_tree.bind("<Double-1>", self._on_invoice_history_double_click)
        self.invoices_tree.bind("<Return>", self._on_invoice_history_double_click)

        self._update_pos_search_results()
        self._refresh_cart_table()
        self._refresh_invoice_history_table()

    def _cfg_cart_cols(self, frame):
        for i, (wt, ms) in enumerate(((4, 190), (1, 75), (2, 105), (1, 75), (1, 75), (1, 90), (1, 50))):
            frame.grid_columnconfigure(i, weight=wt, minsize=ms)

    def _pos_sum_row(self, parent, label_text, default_val, val_color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label_text, text_color="#CBD5E1", font=self.f_r13).pack(side="left")
        lbl = ctk.CTkLabel(row, text=default_val, text_color=val_color, font=self.f_b14)
        lbl.pack(side="right")
        return lbl

    def _on_pos_search_keyrelease(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return", "Escape"):
            return
        if self._pos_search_after_id is not None:
            try:
                self.after_cancel(self._pos_search_after_id)
            except Exception:
                pass
        self._pos_search_after_id = self.after(100, self._update_pos_search_results)

    def _move_pos_sel(self, delta):
        if self._pos_matched_products:
            self._pos_selected_match_idx = (self._pos_selected_match_idx + delta) % len(self._pos_matched_products)
            self._render_pos_suggestion_rows()
        return "break"

    def _on_pos_search_enter(self, _event=None):
        if not self._pos_matched_products:
            messagebox.showwarning("No Matching Product", "No matching product found for your search query.", parent=self)
            return "break"
        idx = max(0, min(self._pos_selected_match_idx, len(self._pos_matched_products) - 1))
        self._add_product_dict_to_cart(self._pos_matched_products[idx])
        self.pos_search_var.set("")
        self._pos_selected_match_idx = 0
        self._update_pos_search_results()
        if hasattr(self, "pos_search_entry") and self.pos_search_entry.winfo_exists():
            self.pos_search_entry.focus_set()
        return "break"

    def _update_pos_search_results(self):
        self._pos_search_after_id = None
        if not (hasattr(self, "pos_suggestions_frame") and self.pos_suggestions_frame.winfo_exists()):
            return
        q = self.pos_search_var.get().strip().lower()
        if not q:
            self._pos_matched_products = [p for p in self._billing_products if p["stock"] > 0][:4]
        else:
            exact = [p for p in self._billing_products if p["sku"].lower() == q]
            part = [p for p in self._billing_products if p not in exact and (q in p["sku"].lower() or q in p["name"].lower() or q in p["category"].lower())]
            self._pos_matched_products = (exact + part)[:5]
        self._pos_selected_match_idx = 0
        self._render_pos_suggestion_rows()

    def _render_pos_suggestion_rows(self):
        if not (hasattr(self, "pos_suggestions_frame") and self.pos_suggestions_frame.winfo_exists()):
            return
        for w in self.pos_suggestions_frame.winfo_children():
            w.destroy()
        if not self._billing_products:
            ctk.CTkLabel(self.pos_suggestions_frame, text="No products in inventory yet. Add or Import CSV on the Inventory page.", text_color=MUTED, font=self.f_r12).pack(padx=12, pady=8)
            return
        if not self._pos_matched_products:
            ctk.CTkLabel(self.pos_suggestions_frame, text="No matching products found. Try searching a different SKU, name, or category.", text_color=RED, font=self.f_r12).pack(padx=12, pady=8)
            return

        for idx, prod in enumerate(self._pos_matched_products):
            sel = idx == self._pos_selected_match_idx
            ir = self._card(self.pos_suggestions_frame, fg_color="#DBEAFE" if sel else WHITE, corner_radius=6, border_color=BLUE if sel else BORDER)
            ir.pack(fill="x", padx=8, pady=3)
            li = ctk.CTkFrame(ir, fg_color="transparent")
            li.pack(side="left", fill="x", expand=True, padx=10, pady=5)
            ctk.CTkLabel(li, text=prod["sku"], fg_color=NAVY if sel else PAGE_BG, text_color=WHITE if sel else TEXT, corner_radius=4, padx=7, pady=1, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(li, text=prod["name"], text_color=TEXT, font=self.f_b12).pack(side="left")
            ctk.CTkLabel(li, text=f"  ({prod['category']})", text_color=MUTED, font=self.f_s11).pack(side="left")

            ri = ctk.CTkFrame(ir, fg_color="transparent")
            ri.pack(side="right", padx=8, pady=4)
            sc = GREEN if prod["stock"] > 10 else (ORANGE if prod["stock"] > 0 else RED)
            ctk.CTkLabel(ri, text=f"Stock: {prod['stock']}" if prod["stock"] > 0 else "Out of Stock", text_color=sc, font=self.f_b12).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(ri, text=f"₹{prod['price']:,.2f}", text_color=TEXT, font=self.f_b12).pack(side="left", padx=(0, 10))
            ctk.CTkButton(ri, text="+ Add" if prod["stock"] > 0 else "No Stock", width=68, height=26, corner_radius=5, fg_color=BLUE if prod["stock"] > 0 else GRAY, hover_color=BLUE_HOVER if prod["stock"] > 0 else GRAY, state="normal" if prod["stock"] > 0 else "disabled", font=ctk.CTkFont(size=11, weight="bold"), command=lambda p=prod: self._add_product_dict_to_cart(p)).pack(side="left")

    def _add_product_dict_to_cart(self, prod):
        if prod["stock"] <= 0:
            messagebox.showwarning("Out of Stock", f"'{prod['name']}' ({prod['sku']}) is currently Out of Stock.", parent=self)
            return
        qty = 1
        if hasattr(self, "bill_qty_entry") and self.bill_qty_entry.winfo_exists():
            try:
                qty = max(1, int(self.bill_qty_entry.get().strip()))
            except ValueError:
                qty = 1
        existing = next((i for i in self.cart_items if i["id"] == prod["id"]), None)
        in_cart = existing["qty"] if existing else 0
        if in_cart + qty > prod["stock"]:
            messagebox.showwarning("Insufficient Stock", f"Cannot add {qty} units of '{prod['name']}'.\nAvailable stock: {prod['stock']} (Already in cart: {in_cart}).", parent=self)
            return
        if existing:
            existing["qty"] += qty
            existing["total"] = existing["qty"] * existing["price"]
        else:
            self.cart_items.append({**prod, "qty": qty, "total": qty * prod["price"]})
        if hasattr(self, "bill_qty_entry") and self.bill_qty_entry.winfo_exists():
            self.bill_qty_entry.delete(0, "end")
            self.bill_qty_entry.insert(0, "1")
        self._refresh_cart_table()

<<<<<<< HEAD
    def _change_cart_item_qty(self, pid, delta):
        target = next((i for i in self.cart_items if i["id"] == pid), None)
=======
    def _change_cart_item_qty(self, product_id, delta):
        target = next((item for item in self.cart_items if item["id"] == product_id), None)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        if not target:
            return
        nq = target["qty"] + delta
        if nq <= 0:
            self.cart_items = [i for i in self.cart_items if i["id"] != pid]
        elif nq > target["stock"]:
            messagebox.showwarning("Stock Limit Reached", f"Only {target['stock']} units of '{target['name']}' available in stock.", parent=self)
            return
        else:
            target["qty"] = nq
            target["total"] = nq * target["price"]
        self._refresh_cart_table()

    def _remove_cart_item_by_id(self, pid):
        self.cart_items = [i for i in self.cart_items if i["id"] != pid]
        self._refresh_cart_table()

    def _clear_cart(self):
        self.cart_items.clear()
        self._refresh_cart_table()

    def _start_new_transaction(self):
        self.cart_items.clear()
        for attr in ("cust_name_entry", "cust_phone_entry"):
            if hasattr(self, attr) and getattr(self, attr).winfo_exists():
                getattr(self, attr).delete(0, "end")
        if hasattr(self, "discount_var"):
            self.discount_var.set(self.app_settings.get("default_discount_pct", "0"))
        if hasattr(self, "invoice_no_var"):
            self.invoice_no_var.set(self._generate_invoice_number())
        self._refresh_cart_table()
        self._shortcut_focus_scan_search()

    def _refresh_cart_table(self):
        if not (hasattr(self, "cart_rows_container") and self.cart_rows_container.winfo_exists()):
            return
        for w in self.cart_rows_container.winfo_children():
            w.destroy()
        b = self._calculate_bill_breakdown()
        if hasattr(self, "cart_badge_label") and self.cart_badge_label.winfo_exists():
            self.cart_badge_label.configure(text=f"{len(self.cart_items)} Items ({b['total_qty']} qty)")

        if not self.cart_items:
            eb = ctk.CTkFrame(self.cart_rows_container, fg_color="transparent")
            eb.pack(fill="both", expand=True, pady=55)
            ctk.CTkLabel(eb, text="🛒 Your shopping cart is empty", font=ctk.CTkFont(size=16, weight="bold"), text_color=MUTED).pack()
            ctk.CTkLabel(eb, text="Scan a SKU/barcode above, press Enter in the search box, or click '+ Add' on any product.", font=self.f_r12, text_color=MUTED).pack(pady=(4, 0))
            self._update_cart_totals()
            return

        dp, tp = b["disc_pct"], b["tax_pct"]
        for item in self.cart_items:
            lsub = item["qty"] * item["price"]
            ldisc = lsub * (dp / 100.0)
            ltaxable = max(0.0, lsub - ldisc)
            ltax = ltaxable * (tp / 100.0)
            lfin = ltaxable + ltax

            rc = self._card(self.cart_rows_container, corner_radius=6)
            rc.pack(fill="x", padx=4, pady=4)
            self._cfg_cart_cols(rc)

            db = ctk.CTkFrame(rc, fg_color="transparent")
            db.grid(row=0, column=0, sticky="w", padx=10, pady=8)
            ctk.CTkLabel(db, text=item["name"], font=self.f_b12, text_color=TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(db, text=f"SKU: {item['sku']}  |  {item['category']}  |  Stock: {item['stock']}", font=self.f_s11, text_color=MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(rc, text=f"₹{item['price']:,.2f}", font=self.f_r12, text_color=TEXT, anchor="e").grid(row=0, column=1, sticky="we", padx=8)

            st = ctk.CTkFrame(rc, fg_color=PAGE_BG, corner_radius=6, border_width=1, border_color=BORDER)
            st.grid(row=0, column=2, padx=8, pady=8)
            ctk.CTkButton(st, text="−", width=26, height=24, corner_radius=4, fg_color="transparent", hover_color=BORDER, text_color=TEXT, font=self.f_b14, command=lambda pid=item["id"]: self._change_cart_item_qty(pid, -1)).pack(side="left", padx=2, pady=2)
            ctk.CTkLabel(st, text=str(item["qty"]), width=28, font=self.f_b12, text_color=TEXT).pack(side="left", padx=2)
            ctk.CTkButton(st, text="+", width=26, height=24, corner_radius=4, fg_color="transparent", hover_color=BORDER, text_color=TEXT, font=self.f_b14, command=lambda pid=item["id"]: self._change_cart_item_qty(pid, 1)).pack(side="left", padx=2, pady=2)

            dbox = ctk.CTkFrame(rc, fg_color="transparent")
            dbox.grid(row=0, column=3, sticky="e", padx=8)
            if dp > 0:
                ctk.CTkLabel(dbox, text=f"-₹{ldisc:,.2f}", font=ctk.CTkFont(size=11, weight="bold"), text_color=ORANGE).pack(anchor="e")
                ctk.CTkLabel(dbox, text=f"{dp:.0f}% OFF", font=ctk.CTkFont(size=10), text_color=MUTED).pack(anchor="e")
            else:
                ctk.CTkLabel(dbox, text="—", font=self.f_r12, text_color=MUTED).pack(anchor="e")

            tbox = ctk.CTkFrame(rc, fg_color="transparent")
            tbox.grid(row=0, column=4, sticky="e", padx=8)
            ctk.CTkLabel(tbox, text=f"+₹{ltax:,.2f}", font=ctk.CTkFont(size=11, weight="bold"), text_color=GREEN).pack(anchor="e")
            ctk.CTkLabel(tbox, text=f"{tp:.0f}% GST", font=ctk.CTkFont(size=10), text_color=MUTED).pack(anchor="e")

            ctk.CTkLabel(rc, text=f"₹{lfin:,.2f}", font=self.f_b12, text_color=TEXT, anchor="e").grid(row=0, column=5, sticky="we", padx=8)
            ctk.CTkButton(rc, text="🗑", width=32, height=28, corner_radius=6, fg_color="transparent", hover_color="#FEE2E2", text_color=RED, font=ctk.CTkFont(size=14), command=lambda pid=item["id"]: self._remove_cart_item_by_id(pid)).grid(row=0, column=6, padx=6)

        self._update_cart_totals()

    def _calculate_bill_breakdown(self):
        subtotal = sum(i["qty"] * i["price"] for i in self.cart_items)
        total_qty = sum(i["qty"] for i in self.cart_items)
        try:
            disc_pct = max(0.0, min(100.0, float((self.discount_var.get().strip() if hasattr(self, "discount_var") else "0") or 0.0)))
        except Exception:
            disc_pct = 0.0
        try:
            tax_pct = max(0.0, float((self.tax_var.get().strip() if hasattr(self, "tax_var") else "18") or 0.0))
        except Exception:
            tax_pct = 0.0
        disc_amt = subtotal * (disc_pct / 100.0)
        taxable = max(0.0, subtotal - disc_amt)
        tax_amt = taxable * (tax_pct / 100.0)
        return {"total_qty": total_qty, "subtotal": subtotal, "disc_pct": disc_pct, "disc_amount": disc_amt, "tax_pct": tax_pct, "tax_amount": tax_amt, "grand_total": taxable + tax_amt}

    def _update_cart_totals(self):
        b = self._calculate_bill_breakdown()
        if hasattr(self, "lbl_items_count") and self.lbl_items_count.winfo_exists():
            self.lbl_items_count.configure(text=f"{len(self.cart_items)} items ({b['total_qty']} qty)")
            self.lbl_subtotal.configure(text=f"₹{b['subtotal']:,.2f}")
            self.lbl_discount.configure(text=f"-₹{b['disc_amount']:,.2f} ({b['disc_pct']:.1f}%)")
            self.lbl_tax.configure(text=f"+₹{b['tax_amount']:,.2f} ({b['tax_pct']:.1f}%)")
            self.lbl_grand_total.configure(text=f"₹{b['grand_total']:,.2f}")
        if hasattr(self, "checkout_btn") and self.checkout_btn.winfo_exists():
            self.checkout_btn.configure(text=f"🛍  Checkout (₹{b['grand_total']:,.2f})  [F10]")

    def _open_quick_discount_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Apply Discount / Coupon")
        win.geometry("360x260")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        ctk.CTkLabel(win, text="Apply Discount (%)", font=self.f_sec, text_color=TEXT).pack(pady=(20, 8))
        ctk.CTkLabel(win, text="Select a preset coupon or enter a custom discount:", text_color=MUTED, font=self.f_r12).pack(pady=(0, 12))
        prow = ctk.CTkFrame(win, fg_color="transparent")
        prow.pack(fill="x", padx=24, pady=(0, 14))

        def apply_pct(val):
            self.discount_var.set(str(val))
            self._refresh_cart_table()
            win.destroy()

        for pct in (0, 5, 10, 15, 20):
            ctk.CTkButton(prow, text=f"{pct}%", width=54, height=34, fg_color=BLUE if pct > 0 else GRAY, hover_color=BLUE_HOVER if pct > 0 else GRAY_HOVER, command=lambda v=pct: apply_pct(v)).pack(side="left", expand=True, padx=3)

        cent = ctk.CTkEntry(win, height=36, placeholder_text="Custom Discount % (e.g. 7.5)")
        cent.pack(fill="x", padx=28, pady=(0, 14))
        cent.insert(0, self.discount_var.get())
        cent.focus_set()

        def apply_custom(_e=None):
            try:
                apply_pct(max(0.0, min(100.0, float(cent.get().strip()))))
            except ValueError:
                messagebox.showerror("Invalid Discount", "Enter a number between 0 and 100.", parent=win)

        cent.bind("<Return>", apply_custom)
        ctk.CTkButton(win, text="Apply Discount", height=38, fg_color=NAVY, hover_color=NAVY_HOVER, command=apply_custom).pack(fill="x", padx=28)

    def _reprint_last_invoice(self):
        invs = self._fetch_recent_invoices(limit=1)
        if not invs:
            messagebox.showinfo("No Invoices Found", "No completed invoices are available to reprint yet.", parent=self)
            return
        self._show_receipt_window(self._build_receipt_data(invs[0]))

    def _show_pos_shortcuts_modal(self):
        win = ctk.CTkToplevel(self)
        win.title("POS Keyboard Shortcuts & Help")
        win.geometry("480x420")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        ctk.CTkLabel(win, text="⌨ POS Terminal Keyboard Shortcuts", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT).pack(pady=(22, 6))
        ctk.CTkLabel(win, text="Speed up billing and checkout using these keyboard controls:", text_color=MUTED, font=self.f_r12).pack(pady=(0, 14))
        lf = self._card(win, corner_radius=8)
        lf.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        for k, d in (
            ("F1", "Start a New Transaction (clears cart & resets form)"),
            ("F2", "Focus the Scan / Product Search bar immediately"),
            ("↑ / ↓ Arrows", "Navigate live product suggestions while searching"),
            ("Enter ↵", "Add highlighted product from search bar to cart"),
            ("F3", "Jump to Recent Invoices history table"),
            ("F4", "Focus Discount (%) box to apply a discount"),
            ("F8", "Reprint / View the most recent invoice receipt"),
            ("F9", "Open this Keyboard Shortcuts help window"),
            ("F10 / Ctrl+Enter", "Complete Sale & Generate Invoice Receipt"),
            ("Esc", "Clear current text in the Scan / Search box"),
        ):
            r = ctk.CTkFrame(lf, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(r, text=k, width=110, fg_color=PAGE_BG, text_color=NAVY, corner_radius=5, font=self.f_b12).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(r, text=d, text_color=TEXT, font=self.f_r12, anchor="w").pack(side="left", fill="x")
        ctk.CTkButton(win, text="Got It", height=38, fg_color=NAVY, hover_color=NAVY_HOVER, command=win.destroy).pack(fill="x", padx=24, pady=(0, 18))

    def _finalize_invoice(self):
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Please add at least one product to the cart before generating an invoice.", parent=self)
            return
        cname = self.cust_name_entry.get().strip() or "Walk-in Customer"
        cphone = self.cust_phone_entry.get().strip()
        pmethod = self.payment_method_var.get()
        inv_no = self.invoice_no_var.get()
        created_at = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
        b = self._calculate_bill_breakdown()

        for item in self.cart_items:
            ok, msg = update_product(item["id"], item["sku"], item["name"], item["category"], max(0, item["stock"] - item["qty"]), item["price"])
            if not ok:
                messagebox.showerror("Stock Update Error", f"Could not update stock for {item['name']}:\n{msg}", parent=self)
                return

        try:
            with self._db_conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO invoices (invoice_no, customer_name, customer_phone, payment_method, subtotal, discount_pct, discount_amount, tax_pct, tax_amount, grand_total, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (inv_no, cname, cphone, pmethod, b["subtotal"], b["disc_pct"], b["disc_amount"], b["tax_pct"], b["tax_amount"], b["grand_total"], created_at),
                )
                inv_id = cur.lastrowid
                cur.executemany(
                    "INSERT INTO invoice_items (invoice_id, product_id, sku, product_name, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [(inv_id, i["id"], i["sku"], i["name"], i["qty"], i["price"], i["qty"] * i["price"]) for i in self.cart_items],
                )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Invoice Error", f"Stock was updated, but saving invoice history failed:\n{exc}", parent=self)
            return

        receipt = {"invoice_no": inv_no, "created_at": created_at, "customer_name": cname, "customer_phone": cphone, "payment_method": pmethod, "items": list(self.cart_items), "breakdown": b}
        self.cart_items.clear()
        self.show_billing()
        self._show_receipt_window(receipt)

    def _refresh_invoice_history_table(self):
        if not (hasattr(self, "invoices_tree") and self.invoices_tree.winfo_exists()):
            return
        self.invoices_tree.delete(*self.invoices_tree.get_children())
        for inv in self._fetch_recent_invoices():
            self.invoices_tree.insert("", "end", values=(inv[0], inv[1], _format_datetime_12h(inv[2]), inv[3], inv[4] or "-", inv[5], inv[6], f"{float(inv[12]):,.2f}"))

    def _on_invoice_history_double_click(self, event=None):
        if not (hasattr(self, "invoices_tree") and self.invoices_tree.winfo_exists()):
            return
        if event and getattr(event, "y", 0) and not self.invoices_tree.identify_row(event.y):
            return
        sel = self.invoices_tree.selection()
        if not sel:
            return
        vals = self.invoices_tree.item(sel[0], "values")
        if not vals:
            return
        target = next((r for r in self._fetch_recent_invoices(limit=200) if int(r[0]) == int(vals[0])), None)
        if target:
            self._show_receipt_window(self._build_receipt_data(target))

    def _format_receipt_text(self, data):
        b, s = data["breakdown"], self.app_settings
        lines = [
            "=" * 56,
            f"{s.get('store_name', 'IMABS').upper()} - {s.get('store_tagline', 'Inventory & Billing System').upper()}".center(56),
            s.get("store_address", "New Delhi, India").center(56),
        ]
        if contact := s.get("store_contact", ""):
            lines.append(contact.center(56))
        lines.extend([
            "=" * 56,
            f"Invoice No : {data['invoice_no']}",
            f"Date       : {_format_datetime_12h(data['created_at'])}",
            f"Customer   : {data['customer_name']}",
            f"Phone      : {data['customer_phone'] or 'N/A'}",
            f"Payment    : {data['payment_method']}",
            "-" * 56,
            f"{'SKU':<10} {'Item':<20} {'Qty':>5} {'Price':>9} {'Total':>9}",
            "-" * 56,
        ])
        for item in data["items"]:
            lt = item.get("total", item["qty"] * item["price"])
            lines.append(f"{str(item['sku'])[:9]:<10} {item['name'][:19]:<20} {item['qty']:>5} {item['price']:>9.2f} {lt:>9.2f}")
        lines.extend([
            "-" * 56,
            f"{'Subtotal:':<40} ₹{b['subtotal']:>12,.2f}",
            f"{('Discount (' + format(b['disc_pct'], '.1f') + '%):'):<40} -₹{b['disc_amount']:>11,.2f}",
            f"{('Tax / GST (' + format(b['tax_pct'], '.1f') + '%):'):<40} +₹{b['tax_amount']:>11,.2f}",
            "=" * 56,
            f"{'GRAND TOTAL:':<40} ₹{b['grand_total']:>12,.2f}",
            "=" * 56,
            "            Thank you for your business!",
            "=" * 56,
        ])
        return "\n".join(lines)

    def _show_receipt_window(self, receipt_data):
        win = ctk.CTkToplevel(self)
        win.title(f"Invoice Receipt - {receipt_data['invoice_no']}")
        win.geometry("540x600")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        ctk.CTkLabel(win, text=f"Invoice {receipt_data['invoice_no']}", font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT).pack(pady=(20, 10))
        rtxt = self._format_receipt_text(receipt_data)
        tb = ctk.CTkTextbox(win, width=480, height=430, font=ctk.CTkFont(family="Courier New", size=12), fg_color=WHITE, text_color=TEXT, border_width=1, border_color=BORDER)
        tb.pack(padx=25, pady=(5, 15))
        tb.insert("1.0", rtxt)
        tb.configure(state="disabled")

        brow = ctk.CTkFrame(win, fg_color="transparent")
        brow.pack(fill="x", padx=25, pady=(0, 20))

        def save_txt():
            path = filedialog.asksaveasfilename(parent=win, title="Save Invoice Receipt", defaultextension=".txt", initialfile=f"{receipt_data['invoice_no']}.txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if path:
                Path(path).write_text(rtxt, encoding="utf-8")
                messagebox.showinfo("Saved", f"Receipt saved to:\n{path}", parent=win)

        ctk.CTkButton(brow, text="💾 Save Receipt (.txt)", fg_color=GREEN, hover_color=GREEN_HOVER, height=40, command=save_txt).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(brow, text="Close", fg_color=NAVY, hover_color=NAVY_HOVER, height=40, command=win.destroy).pack(side="right", expand=True, fill="x", padx=(8, 0))

    def _export_invoices_csv(self):
        invs = self._fetch_recent_invoices(limit=5000)
        if not invs:
            messagebox.showinfo("No Invoices", "There are no invoices to export yet.", parent=self)
            return
        path = filedialog.asksaveasfilename(title="Export Invoices CSV", defaultextension=".csv", initialfile="invoices_export.csv", filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["ID", "Invoice No", "Created At", "Customer Name", "Customer Phone", "Payment Method", "Item Count", "Subtotal", "Discount %", "Discount Amount", "Tax %", "Tax Amount", "Grand Total"])
                for r in invs:
                    w.writerow([r[0], r[1], _format_datetime_12h(r[2]), *r[3:]])
            messagebox.showinfo("Export Complete", f"{len(invs)} invoices exported to:\n{path}", parent=self)
        except Exception as exc:
            messagebox.showerror("Export Error", f"Failed to export invoices:\n{exc}", parent=self)

<<<<<<< HEAD
=======
    # REPORTS 
    =
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    @staticmethod
    def _format_inr_compact(val: float) -> str:
        if val >= 100000:
            return f"₹{val / 100000:.2f}L"
        return f"₹{val / 1000:.1f}K" if val >= 1000 else f"₹{val:.0f}"

    def show_reports(self):
        self.clear_content()
        products, stats = get_products(), get_dashboard_stats()
        cat_qty, cat_val, cat_skus = defaultdict(int), defaultdict(float), defaultdict(int)
        stock_status = {"In Stock": 0, "Low Stock": 0, "Out of Stock": 0}
        restock, total_units = [], 0

        for p in products:
            sku, name, cat, qty, price, st = str(p[1]), str(p[2]), str(p[3]), int(p[4]), float(p[5]), str(p[6])
            total_units += qty
            cat_qty[cat] += qty
            cat_val[cat] += qty * price
            cat_skus[cat] += 1
            stock_status[st] = stock_status.get(st, 0) + 1
            if qty <= 10 or "low" in st.lower() or "out" in st.lower():
                restock.append((sku, name, cat, qty, price, st))
        restock.sort(key=lambda x: (x[3], x[1]))

        total_cats, total_val = len(cat_skus), float(stats.get("total_value", 0.0))
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x")
        tf = ctk.CTkFrame(header, fg_color="transparent")
        tf.pack(side="left")
        ctk.CTkLabel(tf, text="Inventory Analytics & Reports", font=self.f_title, text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(tf, text=f"Executive breakdown across {total_cats} categories and {total_units:,} total units in stock", font=self.f_r13, text_color=MUTED).pack(anchor="w", pady=(2, 0))

        cf = ctk.CTkFrame(header, fg_color="transparent")
        cf.pack(side="right", pady=5)
        if self.report_top_n_var is None:
            self.report_top_n_var = ctk.StringVar(value="Top 8 Categories")
        ctk.CTkLabel(cf, text="Chart View:", text_color=MUTED, font=self.f_r13).pack(side="left", padx=(0, 8))
        ctk.CTkOptionMenu(cf, variable=self.report_top_n_var, values=["Top 5 Categories", "Top 8 Categories", "Top 10 Categories", "Top 12 Categories"], width=155, height=38, fg_color=NAVY, button_color=NAVY, button_hover_color=NAVY_HOVER, command=lambda _c: self.show_reports()).pack(side="left", padx=(0, 10))
        ctk.CTkButton(cf, text="↻ Refresh Reports", width=145, height=38, fg_color=BLUE, hover_color=BLUE_HOVER, command=self.show_reports).pack(side="left")

        try:
            top_n = int(self.report_top_n_var.get().split()[1])
        except Exception:
            top_n = 8

        sf = ctk.CTkFrame(self.content, fg_color="transparent")
        sf.pack(fill="x", pady=(20, 16))
        for i in range(5):
            sf.grid_columnconfigure(i, weight=1)
        for idx, args in enumerate((
            ("TOTAL PRODUCTS", f"{stats.get('total_products', 0)} SKUs", f"Across {total_cats} categories", BLUE),
            ("TOTAL UNITS IN STOCK", f"{total_units:,} Units", "Available physical inventory", NAVY),
            ("TOTAL STOCK VALUE", f"₹{total_val:,.2f}", "Valuation at unit price", GREEN),
            ("LOW STOCK ALERTS", f"{stats.get('low_stock', 0)} Items", "Stock between 1 and 10 units", ORANGE),
            ("OUT OF STOCK", f"{stats.get('out_of_stock', 0)} Items", "Immediate restock required", RED),
        )):
            self.create_report_summary_card(sf, idx, *args)

        rc = ctk.CTkFrame(self.content, fg_color="transparent")
        rc.pack(fill="both", expand=True)
        rc.grid_columnconfigure(0, weight=3)
        rc.grid_columnconfigure(1, weight=2)
        rc.grid_rowconfigure((0, 1), weight=1)

        p1 = self._chart_panel(rc, 0, 0, f"Top {top_n} Categories by Stock Quantity", "Ranked highest to lowest by total physical units in stock")
        self._draw_barh_chart(p1, cat_qty, top_n, "Stock Quantity (Units)", NAVY, BLUE, lambda v: f"{v:,} units", False)

        p2 = self._chart_panel(rc, 0, 1, "Unit Share by Category", "Top 6 categories vs. all remaining categories")
        self._draw_distribution_donut(p2, cat_qty, total_units)

        p3 = self._chart_panel(rc, 1, 0, f"Top {top_n} Categories by Stock Value (₹)", "Highest-value inventory categories (Quantity × Unit Price)")
        self._draw_barh_chart(p3, cat_val, top_n, "Inventory Value (₹)", "#115E59", GREEN, self._format_inr_compact, True)

        p4 = self._chart_panel(rc, 1, 1, "Inventory Health & Stock Status", "Breakdown of In Stock, Low Stock, and Out of Stock SKUs")
        self._draw_status_donut(p4, stock_status)

        tc = ctk.CTkFrame(self.content, fg_color="transparent")
        tc.pack(fill="both", expand=True, pady=(14, 0))
        tc.grid_columnconfigure(0, weight=3)
        tc.grid_columnconfigure(1, weight=2)

        ctp = self._card(tc)
        ctp.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=6)
        ctk.CTkLabel(ctp, text=f"Complete Category Breakdown ({total_cats} Categories)", text_color=TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(15, 2))
        ctk.CTkLabel(ctp, text="Ranked by total inventory value — scroll to inspect every category", text_color=MUTED, font=self.f_s11).pack(anchor="w", padx=20, pady=(0, 6))
        denom = total_val if total_val > 0 else 1.0
        cat_rows = [(i, c, cat_skus[c], f"{cat_qty[c]:,}", f"₹{cat_val[c]:,.2f}", f"{cat_val[c] / denom * 100:.1f}%") for i, c in enumerate(sorted(cat_val, key=cat_val.get, reverse=True), 1)]
        self._simple_table(ctp, (("rank", "#", 40), ("category", "Category Name", 185), ("skus", "SKUs", 65), ("units", "Total Units", 90), ("value", "Stock Value (₹)", 125), ("share", "Value Share", 90)), cat_rows)

        ap = self._card(tc)
        ap.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=6)
        ctk.CTkLabel(ap, text=f"Priority Restock Watchlist ({len(restock)} Items)", text_color=TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(15, 2))
        ctk.CTkLabel(ap, text="Products that are Out of Stock (0) or Low Stock (≤ 10 units)", text_color=MUTED, font=self.f_s11).pack(anchor="w", padx=20, pady=(0, 6))
        alert_rows = [((r[0], r[1], r[3], r[5]), "out" if r[3] <= 0 or "out" in r[5].lower() else "low") for r in restock]
        self._simple_table(ap, (("sku", "SKU", 90), ("name", "Product Name", 195), ("qty", "Stock", 65), ("status", "Alert Status", 105)), alert_rows, tagged=True)

<<<<<<< HEAD
    def _simple_table(self, parent, col_specs, rows, tagged=False):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        tree = ttk.Treeview(frame, columns=[c[0] for c in col_specs], show="headings", style="Inventory.Treeview", height=8)
        for cid, head, w in col_specs:
            tree.heading(cid, text=head)
            tree.column(cid, width=w, anchor="w")
        if tagged:
            tree.tag_configure("out", foreground=RED)
            tree.tag_configure("low", foreground=ORANGE)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.grid(row=0, column=0, sticky="nswe")
        sb.grid(row=0, column=1, sticky="ns")
        for r in rows:
            if tagged:
                tree.insert("", "end", values=r[0], tags=(r[1],))
            else:
                tree.insert("", "end", values=r)
=======
        cat_head = ctk.CTkFrame(cat_table_panel, fg_color="transparent")
        cat_head.pack(fill="x", padx=20, pady=(15, 8))
        ctk.CTkLabel(
            cat_head,
            text=f"Complete Category Breakdown ({total_categories} Categories)",
            text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            cat_head,
            text="Ranked by total inventory value — scroll to inspect every category",
            text_color=MUTED,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(2, 0))

        self._build_category_summary_table(
            cat_table_panel,
            category_sku_count,
            category_quantity,
            category_value,
            total_stock_val
        )

        alert_panel = ctk.CTkFrame(
            tables_container,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        alert_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=6)

        alert_head = ctk.CTkFrame(alert_panel, fg_color="transparent")
        alert_head.pack(fill="x", padx=20, pady=(15, 8))
        ctk.CTkLabel(
            alert_head,
            text=f"Priority Restock Watchlist ({len(restock_items)} Items)",
            text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            alert_head,
            text="Products that are Out of Stock (0) or Low Stock (≤ 10 units)",
            text_color=MUTED,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(2, 0))

        self._build_restock_watchlist_table(alert_panel, restock_items)

    def create_report_summary_card(self, parent, column, title, value, subtext, accent):
        card = ctk.CTkFrame(
            parent,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        card.grid(row=0, column=column, sticky="nsew", padx=5)

        accent_bar = ctk.CTkFrame(
            card,
            width=5,
            height=72,
            corner_radius=3,
            fg_color=accent
        )
        accent_bar.pack(side="left", padx=(12, 10), pady=12)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

    def create_report_summary_card(self, parent, col, title, value, subtext, accent):
        card = self._card(parent)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        ctk.CTkFrame(card, width=5, height=72, corner_radius=3, fg_color=accent).pack(side="left", padx=(12, 10), pady=12)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 10))
        ctk.CTkLabel(info, text=title, text_color=MUTED, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=value, text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(2, 1))
        ctk.CTkLabel(info, text=subtext, text_color=MUTED, font=self.f_s11).pack(anchor="w")

<<<<<<< HEAD
    def _chart_panel(self, parent, row, col, title, subtitle):
        panel = self._card(parent)
        panel.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(panel, text=title, text_color=TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(14, 1))
        ctk.CTkLabel(panel, text=subtitle, text_color=MUTED, font=self.f_s11).pack(anchor="w", padx=20, pady=(0, 2))
        return panel

    def _embed_figure(self, parent, fig):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 12))
=======
        ctk.CTkLabel(
            info,
            text=title,
            text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=value,
            text_color=TEXT,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(2, 1))

        ctk.CTkLabel(
            info,
            text=subtext,
            text_color=MUTED,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w")

    # CHART PANEL
    def create_chart_panel(self, parent, row, column, title, subtitle):
        panel = ctk.CTkFrame(
            parent,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        panel.grid(row=row, column=column, sticky="nsew", padx=6, pady=6)

        heading = ctk.CTkFrame(panel, fg_color="transparent")
        heading.pack(fill="x", padx=20, pady=(14, 2))

        ctk.CTkLabel(
            heading,
            text=title,
            text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            heading,
            text=subtitle,
            text_color=MUTED,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(1, 0))

        return panel

    # CHART 1  HORIZONTAL RANKED BAR - QUANTITY BY CATEGORY
    def create_category_quantity_chart(self, parent, data, top_n=8):
        figure = Figure(figsize=(6.2, 3.2), dpi=90)
        self._active_figures.append(figure)
        figure.patch.set_facecolor(WHITE)
        ax = figure.add_subplot(111)
        ax.set_facecolor(WHITE)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

    def _draw_barh_chart(self, parent, data, top_n, xlabel, top_col, bar_col, fmt_fn, is_inr):
        fig = Figure(figsize=(6.2, 3.2), dpi=90)
        self._active_figures.append(fig)
        fig.patch.set_facecolor(WHITE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(WHITE)
        if not data:
            ax.text(0.5, 0.5, "No inventory data", ha="center", va="center", fontsize=12, color=MUTED)
            ax.axis("off")
        else:
            items = list(reversed(sorted(data.items(), key=lambda x: x[1], reverse=True)[:top_n]))
            cats = [k if len(k) <= 22 else k[:20] + "…" for k, _ in items]
            vals = [v for _, v in items]
            colors = [top_col if i == len(vals) - 1 else bar_col for i in range(len(vals))]
            bars = ax.barh(cats, vals, color=colors, height=0.62, edgecolor="none")
            mv = max(vals) if vals else 1
            ax.set_xlim(0, mv * (1.25 if is_inr else 1.22) if mv > 0 else 10)
            ax.set_xlabel(xlabel, fontsize=9, color=MUTED)
            ax.tick_params(axis="y", labelsize=8.5, colors=TEXT, length=0)
            ax.tick_params(axis="x", labelsize=8, colors=MUTED)
            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1")
            ax.set_axisbelow(True)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            for sp in ("left", "bottom"):
                ax.spines[sp].set_color(BORDER)
            if is_inr:
                ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _p: self._format_inr_compact(x)))
            off = mv * 0.02 if mv > 0 else 0.5
            for bar, v in zip(bars, vals):
                ax.text(bar.get_width() + off, bar.get_y() + bar.get_height() / 2, fmt_fn(v), ha="left", va="center", fontsize=8.5, fontweight="bold", color=TEXT)
        fig.tight_layout(pad=1.2)
        self._embed_figure(parent, fig)

<<<<<<< HEAD
    def _draw_donut(self, parent, values, colors, center_top, center_bot, top_color, legend_labels, startangle):
        fig = Figure(figsize=(5.4, 3.2), dpi=90)
        self._active_figures.append(fig)
        fig.patch.set_facecolor(WHITE)
        ax = fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, "No inventory data", ha="center", va="center", fontsize=12, color=MUTED)
=======
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(BORDER)
            ax.spines["bottom"].set_color(BORDER)

            offset = max_val * 0.02 if max_val > 0 else 0.2
            for bar, value in zip(bars, quantities):
                ax.text(
                    bar.get_width() + offset,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:,} units",
                    ha="left",
                    va="center",
                    fontsize=8.5,
                    fontweight="bold",
                    color=TEXT
                )

        figure.tight_layout(pad=1.2)
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 12))

    # CHART 2: DONUT CHART - STOCK DISTRIBUTION 
    def create_stock_distribution_chart(self, parent, data, total_units=0):
        figure = Figure(figsize=(5.4, 3.2), dpi=90)
        self._active_figures.append(figure)
        figure.patch.set_facecolor(WHITE)
        ax = figure.add_subplot(111)

        filtered = {k: v for k, v in data.items() if v > 0}
        if not filtered:
            ax.text(
                0.5, 0.5, "No inventory data",
                ha="center", va="center", fontsize=12, color=MUTED
            )
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
            ax.axis("off")
        else:
            wedges, _ = ax.pie(values, colors=colors, startangle=startangle, radius=1.0, wedgeprops={"width": 0.42, "edgecolor": WHITE, "linewidth": 2})
            ax.text(0, 0.08, center_top, ha="center", va="center", fontsize=15, fontweight="bold", color=top_color)
            ax.text(0, -0.18, center_bot, ha="center", va="center", fontsize=8.5, color=MUTED)
            ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(0.95, 0.5), frameon=False, fontsize=8, labelcolor=TEXT)
            ax.set_aspect("equal")
        fig.subplots_adjust(left=0.02, right=0.52, top=0.94, bottom=0.06)
        self._embed_figure(parent, fig)

    def _draw_distribution_donut(self, parent, data, total_units):
        items = sorted(((k, v) for k, v in data.items() if v > 0), key=lambda x: x[1], reverse=True)
        labels = [k if len(k) <= 17 else k[:15] + "…" for k, _ in items[:6]]
        vals = [v for _, v in items[:6]]
        if items[6:]:
            labels.append(f"Others ({len(items[6:])} cats)")
            vals.append(sum(v for _, v in items[6:]))
        tot = sum(vals) or 1
        leg = [f"{l}: {v:,} ({v / tot * 100:.1f}%)" for l, v in zip(labels, vals)]
        self._draw_donut(parent, vals, CHART_PALETTE[:len(vals)], f"{total_units:,}", "Total Units", TEXT, leg, 140)

<<<<<<< HEAD
    def _draw_status_donut(self, parent, data):
        cmap = {"In Stock": GREEN, "Low Stock": ORANGE, "Out of Stock": RED}
        labels = [s for s in ("In Stock", "Low Stock", "Out of Stock") if data.get(s, 0) > 0] + [s for s in data if s not in cmap and data[s] > 0]
        vals = [data[s] for s in labels]
        tot = sum(vals) or 1
        pct = f"{data.get('In Stock', 0) / tot * 100:.0f}%"
        leg = [f"{l}: {v} SKUs ({v / tot * 100:.0f}%)" for l, v in zip(labels, vals)]
        self._draw_donut(parent, vals, [cmap.get(s, BLUE) for s in labels], pct, "In Stock", GREEN, leg, 90)

    def show_settings(self):
        self.clear_content()
=======
    # CHART 3: HORIZONTAL RANKED BAR - STOCK VALUE BY CATEGORY
    def create_category_value_chart(self, parent, data, top_n=8):
        figure = Figure(figsize=(6.2, 3.2), dpi=90)
        self._active_figures.append(figure)
        figure.patch.set_facecolor(WHITE)
        ax = figure.add_subplot(111)
        ax.set_facecolor(WHITE)

        if not data:
            ax.text(
                0.5, 0.5, "No inventory data",
                ha="center", va="center", fontsize=12, color=MUTED
            )
            ax.axis("off")
        else:
            sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
            top_items = sorted_items[:top_n]
            categories = [
                (k if len(k) <= 22 else k[:20] + "…") for k, _ in reversed(top_items)
            ]
            values = [v for _, v in reversed(top_items)]

            bar_colors = [
                "#115E59" if i == len(values) - 1 else GREEN
                for i in range(len(values))
            ]
            bars = ax.barh(
                categories,
                values,
                color=bar_colors,
                height=0.62,
                edgecolor="none"
            )

            max_val = max(values) if values else 1.0
            ax.set_xlim(0, max_val * 1.25 if max_val > 0 else 100)
            ax.set_xlabel("Inventory Value (₹)", fontsize=9, color=MUTED)
            ax.tick_params(axis="y", labelsize=8.5, colors=TEXT, length=0)
            ax.tick_params(axis="x", labelsize=8, colors=MUTED)
            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1")
            ax.set_axisbelow(True)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(BORDER)
            ax.spines["bottom"].set_color(BORDER)

            ax.xaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, _pos: self._format_inr_compact(x))
            )

            offset = max_val * 0.02 if max_val > 0 else 1.0
            for bar, value in zip(bars, values):
                ax.text(
                    bar.get_width() + offset,
                    bar.get_y() + bar.get_height() / 2,
                    self._format_inr_compact(value),
                    ha="left",
                    va="center",
                    fontsize=8.5,
                    fontweight="bold",
                    color=TEXT
                )

        figure.tight_layout(pad=1.2)
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 12))

    # CHART 4: DONUT CHART - STOCK AVAILABILITY STATUS
    def create_stock_status_chart(self, parent, data, total_products=0):
        figure = Figure(figsize=(5.4, 3.2), dpi=90)
        self._active_figures.append(figure)
        figure.patch.set_facecolor(WHITE)
        ax = figure.add_subplot(111)

        non_zero = {k: v for k, v in data.items() if v > 0}
        if not non_zero:
            ax.text(
                0.5, 0.5, "No inventory data",
                ha="center", va="center", fontsize=12, color=MUTED
            )
            ax.axis("off")
        else:
            status_order = ["In Stock", "Low Stock", "Out of Stock"]
            status_colors = {
                "In Stock": GREEN,
                "Low Stock": ORANGE,
                "Out of Stock": RED
            }

            labels = [s for s in status_order if data.get(s, 0) > 0]
            for s in data:
                if s not in labels and data[s] > 0:
                    labels.append(s)

            values = [data[s] for s in labels]
            colors = [status_colors.get(s, BLUE) for s in labels]
            total = sum(values) or 1
            in_stock_pct = (data.get("In Stock", 0) / total) * 100.0

            wedges, _ = ax.pie(
                values,
                colors=colors,
                startangle=90,
                radius=1.0,
                wedgeprops={"width": 0.42, "edgecolor": WHITE, "linewidth": 2}
            )

            ax.text(
                0, 0.08,
                f"{in_stock_pct:.0f}%",
                ha="center", va="center",
                fontsize=15, fontweight="bold", color=GREEN
            )
            ax.text(
                0, -0.18,
                "In Stock",
                ha="center", va="center",
                fontsize=8.5, color=MUTED
            )

            legend_labels = [
                f"{lbl}: {val} SKUs ({val / total * 100:.0f}%)"
                for lbl, val in zip(labels, values)
            ]
            ax.legend(
                wedges,
                legend_labels,
                loc="center left",
                bbox_to_anchor=(0.95, 0.5),
                frameon=False,
                fontsize=8.5,
                labelcolor=TEXT
            )
            ax.set_aspect("equal")

        figure.subplots_adjust(left=0.02, right=0.52, top=0.94, bottom=0.06)
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 12))

    def _build_category_summary_table(
        self,
        parent,
        category_sku_count,
        category_quantity,
        category_value,
        total_stock_val
    ):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        cols = ("rank", "category", "skus", "units", "value", "share")
        tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            style="Inventory.Treeview",
            height=8
        )
        headings = {
            "rank": "#",
            "category": "Category Name",
            "skus": "SKUs",
            "units": "Total Units",
            "value": "Stock Value (₹)",
            "share": "Value Share"
        }
        widths = {
            "rank": 40,
            "category": 185,
            "skus": 65,
            "units": 90,
            "value": 125,
            "share": 90
        }
        for col in cols:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nswe")
        scrollbar.grid(row=0, column=1, sticky="ns")

        sorted_cats = sorted(
            category_value.keys(),
            key=lambda c: category_value[c],
            reverse=True
        )
        denom = total_stock_val if total_stock_val > 0 else 1.0
        for idx, cat in enumerate(sorted_cats, start=1):
            val = category_value[cat]
            share_pct = (val / denom) * 100.0
            tree.insert(
                "",
                "end",
                values=(
                    idx,
                    cat,
                    category_sku_count[cat],
                    f"{category_quantity[cat]:,}",
                    f"₹{val:,.2f}",
                    f"{share_pct:.1f}%"
                )
            )

    def _build_restock_watchlist_table(self, parent, restock_items):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        cols = ("sku", "name", "qty", "status")
        tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            style="Inventory.Treeview",
            height=8
        )
        headings = {
            "sku": "SKU",
            "name": "Product Name",
            "qty": "Stock",
            "status": "Alert Status"
        }
        widths = {
            "sku": 90,
            "name": 195,
            "qty": 65,
            "status": "105"
        }
        for col in cols:
            tree.heading(col, text=headings[col])
            tree.column(col, width=int(widths[col]), anchor="w")

        tree.tag_configure("out", foreground=RED)
        tree.tag_configure("low", foreground=ORANGE)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nswe")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for sku, name, _cat, qty, _price, status in restock_items:
            tag = "out" if qty <= 0 or "out" in status.lower() else "low"
            tree.insert(
                "",
                "end",
                values=(sku, name, qty, status),
                tags=(tag,)
            )
   
    # SETTINGS 
    def show_settings(self):
        self.clear_content()

>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(header, text="System Settings & Administration", font=self.f_title, text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Configure store branding, default POS billing rates, stock alert rules, and database backups", text_color=MUTED, font=self.f_r13).pack(anchor="w", pady=(2, 0))

        ws = ctk.CTkFrame(self.content, fg_color="transparent")
        ws.pack(fill="both", expand=True)
        ws.grid_columnconfigure(0, weight=3)
        ws.grid_columnconfigure(1, weight=2)

<<<<<<< HEAD
        lcard = self._card(ws)
        lcard.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(lcard, text="🏪 Store Profile & Billing Defaults", font=self.f_sec, text_color=TEXT).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(lcard, text="These settings appear on generated POS receipts and control alert thresholds", text_color=MUTED, font=self.f_r12).pack(anchor="w", padx=24, pady=(0, 14))
=======
        ctk.CTkLabel(
            title_col,
            text="System Settings & Administration",
            font=self.font_page_title,
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text="Configure store branding, default POS billing rates, stock alert rules, and database backups",
            text_color=MUTED,
            font=self.font_regular_13
        ).pack(anchor="w", pady=(2, 0))

        workspace = ctk.CTkFrame(self.content, fg_color="transparent")
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=3)
        workspace.grid_columnconfigure(1, weight=2)

        left_card = ctk.CTkFrame(
            workspace,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            left_card,
            text="🏪 Store Profile & Billing Defaults",
            font=self.font_section_title,
            text_color=TEXT
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            left_card,
            text="These settings appear on generated POS receipts and control alert thresholds",
            text_color=MUTED,
            font=self.font_regular_12
        ).pack(anchor="w", padx=24, pady=(0, 14))

        form_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=24, pady=(0, 14))
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

        ff = ctk.CTkFrame(lcard, fg_color="transparent")
        ff.pack(fill="x", padx=24, pady=(0, 14))
        ff.grid_columnconfigure((0, 1), weight=1)
        self._settings_entries = {}
        for r, c, key, lbl, span in (
            (0, 0, "store_name", "Store / Brand Name", 1),
            (0, 1, "invoice_prefix", "Invoice Number Prefix (e.g. INV)", 1),
            (1, 0, "store_tagline", "Receipt Subtitle / Tagline", 2),
            (2, 0, "store_address", "Store Location / Address", 2),
            (3, 0, "store_contact", "Store Phone & GSTIN (Printed on Receipt)", 2),
            (4, 0, "default_tax_pct", "Default POS Tax / GST (%)", 1),
            (4, 1, "default_discount_pct", "Default POS Discount (%)", 1),
            (5, 0, "low_stock_threshold", "Low Stock Alert Threshold (Units)", 1),
        ):
            cell = ctk.CTkFrame(ff, fg_color="transparent")
            cell.grid(row=r, column=c, columnspan=span, sticky="we", padx=6, pady=6)
            ctk.CTkLabel(cell, text=lbl, text_color=TEXT, font=self.f_b12, anchor="w").pack(anchor="w", pady=(0, 4))
            ent = ctk.CTkEntry(cell, height=36, border_color=BORDER, fg_color=WHITE)
            ent.pack(fill="x")
            ent.insert(0, str(self.app_settings.get(key, "")))
            self._settings_entries[key] = ent

        bbar = ctk.CTkFrame(lcard, fg_color="transparent")
        bbar.pack(fill="x", padx=30, pady=(10, 22))
        ctk.CTkButton(bbar, text="💾 Save All Settings", height=40, fg_color=BLUE, hover_color=BLUE_HOVER, font=self.f_b12, command=self._on_save_settings_click).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(bbar, text="↺ Restore Defaults", height=40, fg_color=GRAY, hover_color=GRAY_HOVER, font=self.f_b12, command=self._on_restore_default_settings).pack(side="right", expand=True, fill="x", padx=(8, 0))

<<<<<<< HEAD
        db_card = self._card(ws)
        db_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(db_card, text="🗄 Database Health & Diagnostics", font=self.f_sec, text_color=TEXT).pack(anchor="w", padx=24, pady=(20, 6))
=======
        btn_bar = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=30, pady=(10, 22))

        ctk.CTkButton(
            btn_bar,
            text="💾 Save All Settings",
            height=40,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=self.font_bold_12,
            command=self._on_save_settings_click
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btn_bar,
            text="↺ Restore Defaults",
            height=40,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            font=self.font_bold_12,
            command=self._on_restore_default_settings
        ).pack(side="right", expand=True, fill="x", padx=(8, 0))

        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        db_card = ctk.CTkFrame(
            right_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        db_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            db_card,
            text="🗄 Database Health & Diagnostics",
            font=self.font_section_title,
            text_color=TEXT
        ).pack(anchor="w", padx=24, pady=(20, 6))
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

        db_path = self._get_billing_db_path()
        size_kb = db_path.stat().st_size / 1024.0 if db_path.exists() else 0.0
        stats = get_dashboard_stats()
        inv_cnt, total_rev = self._get_sales_summary_stats()

        dbox = ctk.CTkFrame(db_card, fg_color=PAGE_BG, corner_radius=8, border_width=1, border_color=BORDER)
        dbox.pack(fill="x", padx=24, pady=(4, 14))
        for txt, col, fn, py in (
            ("● Status: Connected (SQLite High-Speed Mode)", GREEN, self.f_b12, (10, 4)),
            (f"File: {db_path.name}  ({size_kb:.1f} KB)", TEXT, self.f_r12, 2),
            (f"Records: {stats.get('total_products', 0)} Products  |  {inv_cnt} Invoices", MUTED, self.f_r12, 2),
            (f"Lifetime Billed Revenue: ₹{total_rev:,.2f}", NAVY, self.f_b12, (2, 10)),
        ):
            ctk.CTkLabel(dbox, text=txt, text_color=col, font=fn).pack(anchor="w", padx=14, pady=py)

<<<<<<< HEAD
        ctk.CTkLabel(db_card, text="Backup & Maintenance Tools", font=self.f_b14, text_color=TEXT).pack(anchor="w", padx=24, pady=(4, 8))
        tbox = ctk.CTkFrame(db_card, fg_color="transparent")
        tbox.pack(fill="x", padx=24, pady=(0, 20))
        for txt, fg, hv, cmd in (
            ("💾 Backup Database File (.db)", GREEN, GREEN_HOVER, self._backup_database_file),
            ("⚡ Optimize & Compact Database (VACUUM)", NAVY, NAVY_HOVER, self._optimize_database),
            ("🧹 Clear Invoice History Only", ORANGE, ORANGE_HOVER, self._clear_all_invoice_history),
            ("⚠ Factory Reset All Inventory Products", RED, RED_HOVER, self._factory_reset_inventory),
        ):
            ctk.CTkButton(tbox, text=txt, height=38, fg_color=fg, hover_color=hv, font=self.f_b12, command=cmd).pack(fill="x", pady=4)
=======
        ctk.CTkLabel(
            diag_box,
            text="● Status: Connected (SQLite WAL High-Speed Mode)",
            text_color=GREEN,
            font=self.font_bold_12
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            diag_box,
            text=f"File: {db_path.name}  ({size_kb:.1f} KB)",
            text_color=TEXT,
            font=self.font_regular_12
        ).pack(anchor="w", padx=14, pady=2)

        ctk.CTkLabel(
            diag_box,
            text=f"Records: {stats.get('total_products', 0)} Products  |  {inv_count} Invoices",
            text_color=MUTED,
            font=self.font_regular_12
        ).pack(anchor="w", padx=14, pady=2)

        ctk.CTkLabel(
            diag_box,
            text=f"Lifetime Billed Revenue: ₹{total_rev:,.2f}",
            text_color=NAVY,
            font=self.font_bold_12
        ).pack(anchor="w", padx=14, pady=(2, 10))

        ctk.CTkLabel(
            db_card,
            text="Backup & Maintenance Tools",
            font=self.font_bold_14,
            text_color=TEXT
        ).pack(anchor="w", padx=24, pady=(4, 8))

        tools_box = ctk.CTkFrame(db_card, fg_color="transparent")
        tools_box.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkButton(
            tools_box,
            text="💾 Backup Database File (.db)",
            height=38,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            font=self.font_bold_12,
            command=self._backup_database_file
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            tools_box,
            text="⚡ Optimize & Compact Database (VACUUM)",
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            font=self.font_bold_12,
            command=self._optimize_database
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            tools_box,
            text="🧹 Clear Invoice History Only",
            height=38,
            fg_color=ORANGE,
            hover_color=ORANGE_HOVER,
            font=self.font_bold_12,
            command=self._clear_all_invoice_history
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            tools_box,
            text="⚠ Factory Reset All Inventory Products",
            height=38,
            fg_color=RED,
            hover_color=RED_HOVER,
            font=self.font_bold_12,
            command=self._factory_reset_inventory
        ).pack(fill="x", pady=4)
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e

    def _on_save_settings_click(self):
        vals = {k: e.get().strip() for k, e in self._settings_entries.items()}
        if not vals.get("store_name"):
            messagebox.showwarning("Validation", "Store Name cannot be empty.", parent=self)
            return
        try:
            tf, df, ti = float(vals.get("default_tax_pct", "18")), float(vals.get("default_discount_pct", "0")), int(float(vals.get("low_stock_threshold", "10")))
            if tf < 0 or df < 0 or df > 100 or ti < 1:
                raise ValueError
            vals["default_tax_pct"], vals["default_discount_pct"], vals["low_stock_threshold"] = str(tf), str(df), str(ti)
        except ValueError:
            messagebox.showerror("Invalid Numeric Setting", "Tax % (≥ 0), Discount % (0–100), and Low Stock Threshold (≥ 1) must be valid numbers.", parent=self)
            return
        self._save_app_settings(vals)
        messagebox.showinfo("Settings Saved", "Store profile, billing defaults, and stock alert thresholds have been updated.", parent=self)
        self.show_settings()

    def _on_restore_default_settings(self):
        if messagebox.askyesno("Restore Default Settings", "Restore all store and billing settings to their default values?", parent=self):
            self._save_app_settings(self._default_settings())
            self.show_settings()

    def _backup_database_file(self):
        db_path = self._get_billing_db_path()
        if not db_path.exists():
            messagebox.showwarning("No Database", "Database file does not exist yet.", parent=self)
            return
        stamp = datetime.now().strftime("%d%m%Y_%I%M%S%p")
        dest = filedialog.asksaveasfilename(title="Save Database Backup", defaultextension=".db", initialfile=f"inventory_backup_{stamp}.db", filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")])
        if not dest:
            return
        try:
            shutil.copy2(str(db_path), str(dest))
            messagebox.showinfo("Backup Complete", f"Database backup saved successfully to:\n{dest}", parent=self)
        except Exception as exc:
            messagebox.showerror("Backup Error", f"Could not back up database:\n{exc}", parent=self)

    def _optimize_database(self):
        try:
            with self._db_conn() as conn:
                conn.execute("VACUUM;")
                conn.execute("ANALYZE;")
            messagebox.showinfo("Optimization Complete", "SQLite VACUUM and ANALYZE completed. Database storage is compacted and indexed for fast queries.", parent=self)
            self.show_settings()
        except Exception as exc:
            messagebox.showerror("Optimization Error", str(exc), parent=self)

    def _clear_all_invoice_history(self):
        if not messagebox.askyesno("Clear Invoice History", "Are you sure you want to delete all past invoices and billing history?\n\nYour inventory products will NOT be deleted.", parent=self):
            return
        try:
            with self._db_conn() as conn:
                conn.execute("DELETE FROM invoice_items;")
                conn.execute("DELETE FROM invoices;")
                conn.commit()
            messagebox.showinfo("Cleared", "All invoice history has been cleared.", parent=self)
            self.show_settings()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _factory_reset_inventory(self):
        if not messagebox.askyesno("Factory Reset Inventory", "WARNING: This will permanently delete ALL products from your inventory database!\n\nAre you sure you want to continue?", parent=self):
            return
        try:
            with self._db_conn() as conn:
                conn.execute("DELETE FROM products;")
                conn.commit()
            self.cart_items.clear()
            messagebox.showinfo("Reset Complete", "All inventory products have been removed.", parent=self)
            self.show_settings()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

<<<<<<< HEAD
=======
    # CREATE INVOICE 
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
    def create_invoice(self):
        self.show_page("Billing")
        self._shortcut_focus_scan_search()

<<<<<<< HEAD

=======
# RUN APPLICATION
>>>>>>> 77512603df9b315f40e2f44f75c5a61ec1ba644e
if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
