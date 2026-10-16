import sys
import csv
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================
# FIX IMPORT PATH
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

# ============================================================
# IMPORTS
# ============================================================
import tkinter as tk
import customtkinter as ctk
from tkinter import (
    ttk,
    filedialog,
    messagebox
)
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
import tempfile
import database as _db_module
from database import (
    initialize_database,
    add_product,
    get_products,
    search_products,
    update_product,
    delete_product,
    get_dashboard_stats,
    import_products_from_csv,
    export_products_to_csv
)


def _ensure_writable_sqlite_path() -> Path:
    """
    Ensure SQLite can open and write to the database file even when the project
    is stored inside a Windows OneDrive or Unicode folder (e.g. OneDrive\\ドキュメント\\Desktop)
    or a folder protected by Windows Controlled Folder Access.
    """
    script_dir = Path(__file__).resolve().parent
    candidates = []
    if hasattr(_db_module, "DB_PATH"):
        candidates.append(Path(getattr(_db_module, "DB_PATH")))
    candidates.extend([
        script_dir / "Database" / "inventory.db",
        script_dir / "inventory.db",
    ])
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "IMABS" / "Database" / "inventory.db")
    candidates.extend([
        Path.home() / "IMABS_Data" / "inventory.db",
        Path(tempfile.gettempdir()) / "IMABS" / "inventory.db",
    ])

    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(candidate))
            conn.execute("CREATE TABLE IF NOT EXISTS _db_check (id INTEGER);")
            conn.commit()
            conn.close()
            # Patch database module globals so all CRUD calls use this verified path
            _db_module.DB_PATH = candidate
            _db_module.DB_FOLDER = candidate.parent

            def _safe_get_connection(_target=candidate):
                _target.parent.mkdir(parents=True, exist_ok=True)
                c = sqlite3.connect(str(_target))
                try:
                    c.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.Error:
                    try:
                        c.execute("PRAGMA journal_mode=DELETE;")
                    except sqlite3.Error:
                        pass
                try:
                    c.execute("PRAGMA synchronous=NORMAL;")
                    c.execute("PRAGMA foreign_keys=ON;")
                except sqlite3.Error:
                    pass
                return c

            _db_module.get_connection = _safe_get_connection
            return candidate
        except Exception:
            continue

    fallback = Path(tempfile.gettempdir()) / "inventory.db"
    _db_module.DB_PATH = fallback
    _db_module.DB_FOLDER = fallback.parent
    return fallback


ACTIVE_DB_PATH = _ensure_writable_sqlite_path()

# ============================================================
# APPEARANCE
# ============================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ============================================================
# COLORS (ORIGINAL THEME STRICTLY PRESERVED)
# ============================================================
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

# Cohesive chart palette matching the app's Navy/Blue/Teal/Amber/Slate theme
CHART_PALETTE = [
    "#2563EB",  # Primary Blue
    "#0F766E",  # Teal Green
    "#1E40AF",  # Deep Blue
    "#0D9488",  # Bright Teal
    "#3B82F6",  # Sky Blue
    "#D97706",  # Amber Orange
    "#64748B",  # Slate Muted (for "Others")
]


# ============================================================
# SIDEBAR BUTTON (OPTIMIZED WITH CACHED FONTS)
# ============================================================
class SidebarButton(ctk.CTkButton):
    _font_normal = None
    _font_bold = None

    def __init__(self, master, text, command=None):
        if SidebarButton._font_normal is None:
            SidebarButton._font_normal = ctk.CTkFont(size=14)
            SidebarButton._font_bold = ctk.CTkFont(size=14, weight="bold")

        super().__init__(
            master,
            text=text,
            command=command,
            anchor="w",
            height=42,
            corner_radius=7,
            fg_color="transparent",
            hover_color=NAVY_HOVER,
            text_color=WHITE,
            font=SidebarButton._font_normal
        )

    def set_active(self, active):
        if active:
            self.configure(
                fg_color=NAVY_HOVER,
                font=SidebarButton._font_bold
            )
        else:
            self.configure(
                fg_color="transparent",
                font=SidebarButton._font_normal
            )


# ============================================================
# DASHBOARD APPLICATION
# ============================================================
class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # STATE & PERFORMANCE CACHE FOR OLDER SYSTEMS
        # ----------------------------------------------------
        self.current_page = "Dashboard"
        self.inventory_tree = None
        self.dashboard_tree = None
        self._search_after_id = None
        self._pos_search_after_id = None
        self._active_figures = []
        self.cart_items = []  # List of dicts: {id, sku, name, category, stock, qty, price, total}
        self._pos_matched_products = []
        self._pos_selected_match_idx = 0
        self.report_top_n_var = None

        # Dashboard & Inventory filter states
        self.dashboard_status_filter = "All"
        self.inv_category_filter_var = None
        self.inv_status_filter_var = None
        self.inv_sort_var = None

        # ----------------------------------------------------
        # DATABASE & PERSISTENT SETTINGS
        # ----------------------------------------------------
        initialize_database()
        self._init_billing_and_settings_tables()
        self.app_settings = self._load_app_settings()

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------
        self.title(f"{self.app_settings['store_name']} - Inventory Management System")
        self.geometry("1400x830")
        self.minsize(1100, 650)
        self.configure(fg_color=PAGE_BG)

        # Cache common fonts once to avoid recreating font objects on older CPUs
        self.font_page_title = ctk.CTkFont(size=30, weight="bold")
        self.font_section_title = ctk.CTkFont(size=18, weight="bold")
        self.font_card_title = ctk.CTkFont(size=12, weight="bold")
        self.font_card_value = ctk.CTkFont(size=24, weight="bold")
        self.font_bold_14 = ctk.CTkFont(size=14, weight="bold")
        self.font_bold_12 = ctk.CTkFont(size=12, weight="bold")
        self.font_regular_13 = ctk.CTkFont(size=13)
        self.font_regular_12 = ctk.CTkFont(size=12)
        self.font_small_11 = ctk.CTkFont(size=11)

        # Configure ttk Treeview styles once at startup
        self._setup_treeview_styles()

        # Bind global POS keyboard shortcuts (active when on Billing page)
        self._bind_pos_keyboard_shortcuts()

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # BUILD GUI
        # ----------------------------------------------------
        self.build_sidebar()
        self.build_main_area()

        # ----------------------------------------------------
        # START DASHBOARD
        # ----------------------------------------------------
        self.show_page("Dashboard")

    # ========================================================
    # KEYBOARD SHORTCUTS FOR POS BILLING TERMINAL
    # ========================================================
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

    def _shortcut_add_product(self, event=None):
        if self.current_page in ("Dashboard", "Inventory"):
            self.open_add_product()

    def _shortcut_delete_selected_product(self, event=None):
        if self.current_page == "Inventory" and self.inventory_tree is not None and self.inventory_tree.winfo_exists():
            if self.inventory_tree.selection():
                self.delete_selected_product()

    def _shortcut_new_transaction(self, event=None):
        if self.current_page != "Billing":
            return
        self._start_new_transaction()

    def _shortcut_focus_scan_search(self, event=None):
        if self.current_page != "Billing":
            self.show_page("Billing")
        if hasattr(self, "pos_search_entry") and self.pos_search_entry.winfo_exists():
            self.pos_search_entry.focus_set()
            self.pos_search_entry.select_range(0, "end")

    def _shortcut_focus_invoice_history(self, event=None):
        if self.current_page != "Billing":
            return
        if hasattr(self, "invoices_tree") and self.invoices_tree.winfo_exists():
            children = self.invoices_tree.get_children()
            if children:
                self.invoices_tree.focus_set()
                self.invoices_tree.selection_set(children[0])
                self.invoices_tree.focus(children[0])

    def _shortcut_focus_discount(self, event=None):
        if self.current_page != "Billing":
            return
        if hasattr(self, "discount_entry") and self.discount_entry.winfo_exists():
            self.discount_entry.focus_set()
            self.discount_entry.select_range(0, "end")

    def _shortcut_reprint_last_receipt(self, event=None):
        if self.current_page != "Billing":
            return
        self._reprint_last_invoice()

    def _shortcut_show_help(self, event=None):
        if self.current_page != "Billing":
            return
        self._show_pos_shortcuts_modal()

    def _shortcut_checkout(self, event=None):
        if self.current_page != "Billing":
            return
        self._finalize_invoice()

    def _shortcut_escape(self, event=None):
        if self.current_page != "Billing":
            return
        if hasattr(self, "pos_search_var") and self.pos_search_var.get().strip():
            self.pos_search_var.set("")
            self._update_pos_search_results()
            if hasattr(self, "pos_search_entry") and self.pos_search_entry.winfo_exists():
                self.pos_search_entry.focus_set()

    # ========================================================
    # TREEVIEW STYLE INITIALIZATION (RUNS ONCE)
    # ========================================================
    def _setup_treeview_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Inventory.Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=TEXT,
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Inventory.Treeview.Heading",
            background=BORDER,
            foreground=TEXT,
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Inventory.Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", TEXT)]
        )
        style.map(
            "Inventory.Treeview.Heading",
            background=[("active", "#CBD5E1")]
        )

    # ========================================================
    # SQLITE STORAGE FOR BILLING & APP SETTINGS
    # ========================================================
    def _get_billing_db_path(self):
        if hasattr(_db_module, "DB_PATH"):
            p = Path(getattr(_db_module, "DB_PATH"))
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                return p
            except Exception:
                pass
        return _ensure_writable_sqlite_path()

    def _init_billing_and_settings_tables(self):
        """Ensure billing/invoice and app_settings tables exist inside inventory.db."""
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute(
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
                conn.execute(
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
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception:
            pass

    def _default_settings(self):
        return {
            "store_name": "IMABS",
            "store_tagline": "Inventory & Billing Management System",
            "store_address": "New Delhi, India",
            "store_contact": "+91 9876543210  |  GSTIN: 07AAAAA0000A1Z5",
            "default_tax_pct": "18",
            "default_discount_pct": "0",
            "low_stock_threshold": "10",
            "currency_symbol": "₹",
            "invoice_prefix": "INV",
        }

    def _load_app_settings(self):
        defaults = self._default_settings()
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute("SELECT key, value FROM app_settings")
                for k, v in cur.fetchall():
                    if k in defaults and v is not None:
                        defaults[k] = str(v)
        except Exception:
            pass
        return defaults

    def _save_app_settings(self, new_settings: dict):
        db_path = self._get_billing_db_path()
        with sqlite3.connect(str(db_path)) as conn:
            cur = conn.cursor()
            for k, v in new_settings.items():
                cur.execute(
                    """
                    INSERT INTO app_settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (str(k), str(v)),
                )
            # Also recalculate product statuses against the new low_stock_threshold
            try:
                threshold = max(1, int(float(new_settings.get("low_stock_threshold", 10))))
                cur.execute(
                    """
                    UPDATE products
                    SET status = CASE
                        WHEN quantity <= 0 THEN 'Out of Stock'
                        WHEN quantity <= ? THEN 'Low Stock'
                        ELSE 'In Stock'
                    END
                    """,
                    (threshold,),
                )
            except Exception:
                pass
            conn.commit()
        self.app_settings = self._load_app_settings()
        if hasattr(self, "sidebar_logo") and self.sidebar_logo.winfo_exists():
            self.sidebar_logo.configure(text=self.app_settings["store_name"][:12])
        self.title(f"{self.app_settings['store_name']} - Inventory Management System")

    def _get_sales_summary_stats(self):
        """Return (invoice_count, total_revenue) from invoices table."""
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT COUNT(*), COALESCE(SUM(grand_total), 0.0) FROM invoices"
                )
                row = cur.fetchone()
                if row:
                    return int(row[0] or 0), float(row[1] or 0.0)
        except Exception:
            pass
        return 0, 0.0

    def _generate_invoice_number(self):
        prefix = self.app_settings.get("invoice_prefix", "INV").strip() or "INV"
        now_str = datetime.now().strftime("%Y%m%d")
        db_path = self._get_billing_db_path()
        count = 1
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM invoices")
                row = cur.fetchone()
                if row and row[0] is not None:
                    count = int(row[0]) + 1
        except Exception:
            pass
        return f"{prefix}-{now_str}-{count:04d}"

    def _generate_next_sku(self):
        """Generate the next sequential SKU (e.g., SKU-1029) for Add Product."""
        products = get_products()
        max_num = 1000
        for p in products:
            sku_str = str(p[1])
            digits = "".join(ch for ch in sku_str if ch.isdigit())
            if digits:
                try:
                    num = int(digits)
                    if 1 <= num <= 999999:
                        max_num = max(max_num, num)
                except ValueError:
                    pass
        return f"SKU-{max_num + 1}"

    def _fetch_recent_invoices(self, limit=50):
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                        i.id,
                        i.invoice_no,
                        i.created_at,
                        i.customer_name,
                        i.customer_phone,
                        i.payment_method,
                        COUNT(ii.id) AS item_count,
                        i.subtotal,
                        i.discount_pct,
                        i.discount_amount,
                        i.tax_pct,
                        i.tax_amount,
                        i.grand_total
                    FROM invoices i
                    LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
                    GROUP BY i.id
                    ORDER BY i.id DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                return cur.fetchall()
        except Exception:
            return []

    def _fetch_invoice_items(self, invoice_id):
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT sku, product_name, quantity, unit_price, line_total
                    FROM invoice_items
                    WHERE invoice_id = ?
                    ORDER BY id ASC
                    """,
                    (int(invoice_id),)
                )
                return cur.fetchall()
        except Exception:
            return []

    # ========================================================
    # SIDEBAR
    # ========================================================
    def build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=180,
            corner_radius=0,
            fg_color=NAVY
        )
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_propagate(False)

        self.sidebar_logo = ctk.CTkLabel(
            sidebar,
            text=self.app_settings.get("store_name", "IMABS")[:12],
            text_color=WHITE,
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.sidebar_logo.pack(pady=(35, 45))

        self.nav_buttons = {}
        nav_items = [
            "Dashboard",
            "Inventory",
            "Billing",
            "Reports",
            "Settings"
        ]
        for item in nav_items:
            button = SidebarButton(
                sidebar,
                text=item,
                command=lambda name=item: self.show_page(name)
            )
            button.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[item] = button

    # ========================================================
    # MAIN AREA
    # ========================================================
    def build_main_area(self):
        self.main = ctk.CTkFrame(
            self,
            fg_color=PAGE_BG,
            corner_radius=0
        )
        self.main.grid(row=0, column=1, sticky="nswe")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        topbar = ctk.CTkFrame(
            self.main,
            height=70,
            fg_color=WHITE,
            corner_radius=0
        )
        topbar.grid(row=0, column=0, sticky="we")
        topbar.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            topbar,
            width=380,
            height=38,
            placeholder_text="Search inventory by SKU, name, or category...",
            textvariable=self.search_var,
            border_color="#94A3B8"
        )
        self.search_entry.grid(
            row=0,
            column=0,
            padx=35,
            pady=16,
            sticky="w"
        )
        self.search_entry.bind("<KeyRelease>", self._on_search_keyrelease)

        invoice_button = ctk.CTkButton(
            topbar,
            text="+ Create Invoice",
            width=140,
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            command=self.create_invoice
        )
        invoice_button.grid(row=0, column=1, padx=30)

        self.content = ctk.CTkScrollableFrame(
            self.main,
            fg_color=PAGE_BG,
            corner_radius=0
        )
        self.content.grid(
            row=1,
            column=0,
            sticky="nswe",
            padx=35,
            pady=25
        )
        self.content.grid_columnconfigure(0, weight=1)

    # ========================================================
    # CLEAR CONTENT & MEMORY CLEANUP
    # ========================================================
    def clear_content(self):
        self.inventory_tree = None
        self.dashboard_tree = None

        for fig in self._active_figures:
            try:
                fig.clear()
            except Exception:
                pass
        self._active_figures.clear()

        for widget in self.content.winfo_children():
            widget.destroy()

    # ========================================================
    # PAGE NAVIGATION
    # ========================================================
    def show_page(self, page):
        self.current_page = page
        for name, button in self.nav_buttons.items():
            button.set_active(name == page)

        self.clear_content()

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

    # ========================================================
    # REDESIGNED DASHBOARD (EXECUTIVE COMMAND CENTER)
    # ========================================================
    def show_dashboard(self):
        self.clear_content()

        # ----------------------------------------------------
        # 1. HEADER WITH QUICK-ACTION TOOLBAR
        # ----------------------------------------------------
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left")

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

        # ----------------------------------------------------
        # 2. 5 EXECUTIVE KPI CARDS (WITH ACCENT BARS)
        # ----------------------------------------------------
        stats = get_dashboard_stats()
        all_products = get_products()
        total_units = sum(int(p[4]) for p in all_products)
        total_categories = len({str(p[3]) for p in all_products})
        invoice_count, total_revenue = self._get_sales_summary_stats()
        threshold = self.app_settings.get("low_stock_threshold", "10")

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 18))
        for i in range(5):
            cards.grid_columnconfigure(i, weight=1)

        self.create_report_summary_card(
            cards,
            0,
            "TOTAL STOCK VALUE",
            f"₹{stats.get('total_value', 0.0):,.2f}",
            f"{total_units:,} total units in stock",
            BLUE
        )
        self.create_report_summary_card(
            cards,
            1,
            "TOTAL SALES REVENUE",
            f"₹{total_revenue:,.2f}",
            f"Across {invoice_count} completed invoices",
            GREEN
        )
        self.create_report_summary_card(
            cards,
            2,
            "ACTIVE CATALOG",
            f"{stats.get('total_products', 0)} Products",
            f"Spanning {total_categories} categories",
            NAVY
        )
        self.create_report_summary_card(
            cards,
            3,
            "LOW STOCK ALERTS",
            f"{stats.get('low_stock', 0)} Items",
            f"Stock ≤ {threshold} units threshold",
            ORANGE
        )
        self.create_report_summary_card(
            cards,
            4,
            "OUT OF STOCK",
            f"{stats.get('out_of_stock', 0)} Items",
            "0 units — Immediate restock",
            RED
        )

        # ----------------------------------------------------
        # 3. TWO-COLUMN MAIN DASHBOARD WORKSPACE
        # ----------------------------------------------------
        workspace = ctk.CTkFrame(self.content, fg_color="transparent")
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=7)
        workspace.grid_columnconfigure(1, weight=3)

        # LEFT PANEL: LIVE INVENTORY EXPLORER WITH STATUS FILTER PILLS
        left_panel = ctk.CTkFrame(
            workspace,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

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

        # Status Filter Pills (All | In Stock | Low Stock | Out of Stock)
        filter_bar = ctk.CTkFrame(left_top, fg_color="transparent")
        filter_bar.pack(side="right")

        for status_opt in ("All", "In Stock", "Low Stock", "Out of Stock"):
            is_active = (self.dashboard_status_filter == status_opt)
            pill_color = NAVY if is_active else PAGE_BG
            pill_text_color = WHITE if is_active else TEXT
            ctk.CTkButton(
                filter_bar,
                text=status_opt,
                width=84,
                height=30,
                corner_radius=6,
                fg_color=pill_color,
                hover_color=NAVY_HOVER if is_active else BORDER,
                text_color=pill_text_color,
                font=self.font_bold_12 if is_active else self.font_regular_12,
                command=lambda s=status_opt: self._set_dashboard_status_filter(s)
            ).pack(side="left", padx=3)

        query = self.search_var.get().strip()
        filtered_products = self._get_filtered_dashboard_products(query)
        self.dashboard_tree = self.create_inventory_table(
            left_panel,
            filtered_products,
            height=13,
            include_total_value=True
        )
        self.dashboard_tree.bind("<Double-1>", self._on_dashboard_tree_double_click)

        # RIGHT PANEL: STACKED ACTION CARDS (1-CLICK RESTOCK + RECENT SALES)
        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Card A: Priority Restock Action Center (1-Click +10 Stock)
        restock_card = ctk.CTkFrame(
            right_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        restock_card.pack(fill="both", expand=True, pady=(0, 12))

        r_head = ctk.CTkFrame(restock_card, fg_color="transparent")
        r_head.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            r_head,
            text="⚡ Quick Restock Alerts",
            text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        alert_products = [
            p for p in all_products
            if int(p[4]) <= 0 or "low" in str(p[6]).lower() or "out" in str(p[6]).lower()
        ]
        alert_products.sort(key=lambda x: int(x[4]))

        ctk.CTkLabel(
            r_head,
            text=f"{len(alert_products)} Alerts",
            fg_color="#FEF3C7" if alert_products else "#DCFCE7",
            text_color=ORANGE if alert_products else GREEN,
            corner_radius=10,
            padx=10,
            pady=2,
            font=self.font_bold_12
        ).pack(side="right")

        ctk.CTkLabel(
            restock_card,
            text="Click '+10' to instantly replenish low or out-of-stock items:",
            text_color=MUTED,
            font=self.font_small_11
        ).pack(anchor="w", padx=18, pady=(0, 6))

        restock_list = ctk.CTkScrollableFrame(
            restock_card,
            fg_color=PAGE_BG,
            corner_radius=8,
            height=175
        )
        restock_list.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        if not alert_products:
            ctk.CTkLabel(
                restock_list,
                text="✓ All products are well-stocked!",
                text_color=GREEN,
                font=self.font_bold_12
            ).pack(pady=35)
        else:
            for prod in alert_products[:12]:
                p_id, sku, name, cat, qty, price, status = prod
                is_out = int(qty) <= 0
                row_f = ctk.CTkFrame(
                    restock_list,
                    fg_color=WHITE,
                    corner_radius=6,
                    border_width=1,
                    border_color=BORDER
                )
                row_f.pack(fill="x", padx=4, pady=3)

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

        # Card B: Recent Sales / Invoices Activity Feed
        sales_card = ctk.CTkFrame(
            right_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        sales_card.pack(fill="both", expand=True)

        s_head = ctk.CTkFrame(sales_card, fg_color="transparent")
        s_head.pack(fill="x", padx=18, pady=(14, 6))

        ctk.CTkLabel(
            s_head,
            text="🧾 Recent Sales Activity",
            text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            s_head,
            text="Open POS →",
            width=88,
            height=26,
            corner_radius=5,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.show_page("Billing")
        ).pack(side="right")

        recent_invs = self._fetch_recent_invoices(limit=5)
        sales_list = ctk.CTkFrame(sales_card, fg_color=PAGE_BG, corner_radius=8)
        sales_list.pack(fill="both", expand=True, padx=16, pady=(4, 14))

        if not recent_invs:
            ctk.CTkLabel(
                sales_list,
                text="No invoices generated yet.\nClick '+ Create Invoice' to start billing.",
                text_color=MUTED,
                font=self.font_regular_12
            ).pack(pady=30)
        else:
            for inv in recent_invs:
                inv_row = ctk.CTkFrame(
                    sales_list,
                    fg_color=WHITE,
                    corner_radius=6,
                    border_width=1,
                    border_color=BORDER
                )
                inv_row.pack(fill="x", padx=6, pady=3)

                l_col = ctk.CTkFrame(inv_row, fg_color="transparent")
                l_col.pack(side="left", padx=8, pady=5)

                ctk.CTkLabel(
                    l_col,
                    text=f"{inv[1]}  •  {inv[3]}",
                    text_color=TEXT,
                    font=self.font_bold_12
                ).pack(anchor="w")

                ctk.CTkLabel(
                    l_col,
                    text=f"{inv[2]}  |  {inv[5]} ({inv[6]} items)",
                    text_color=MUTED,
                    font=self.font_small_11
                ).pack(anchor="w")

                ctk.CTkLabel(
                    inv_row,
                    text=f"₹{float(inv[12]):,.2f}",
                    text_color=GREEN,
                    font=self.font_bold_12
                ).pack(side="right", padx=10)

    def _set_dashboard_status_filter(self, status_choice):
        self.dashboard_status_filter = status_choice
        self.show_dashboard()

    def _get_filtered_dashboard_products(self, query=""):
        products = search_products(query) if query else get_products()
        if self.dashboard_status_filter == "All":
            return products
        target = self.dashboard_status_filter.lower()
        return [p for p in products if str(p[6]).lower() == target]

    def _on_dashboard_tree_double_click(self, event=None):
        if self.dashboard_tree is None or not self.dashboard_tree.winfo_exists():
            return
        if event is not None:
            clicked_row = self.dashboard_tree.identify_row(event.y)
            if not clicked_row:
                return
        selected = self.dashboard_tree.selection()
        if not selected:
            return
        values = self.dashboard_tree.item(selected[0], "values")
        if values:
            self.open_edit_product(values)

    def _quick_restock_product(self, prod, add_qty=10):
        p_id, sku, name, cat, qty, price, _status = prod
        new_qty = int(qty) + int(add_qty)
        ok, msg = update_product(int(p_id), str(sku), str(name), str(cat), new_qty, float(price))
        if ok:
            if self.current_page == "Dashboard":
                self.show_dashboard()
            elif self.current_page == "Inventory":
                self.refresh_inventory()
        else:
            messagebox.showerror("Restock Error", msg, parent=self)

    # ========================================================
    # STAT CARD
    # ========================================================
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

    # ========================================================
    # REDESIGNED INVENTORY PAGE (FILTER, SORT & STOCK CONTROL)
    # ========================================================
    def show_inventory(self):
        self.clear_content()

        # ----------------------------------------------------
        # 1. HEADER & ACTION BUTTONS BAR
        # ----------------------------------------------------
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left")

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

        # ----------------------------------------------------
        # 2. FILTER, SORT & BULK CONTROL BAR CARD
        # ----------------------------------------------------
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

        self.inv_category_filter_var = ctk.StringVar(value="All Categories")
        cat_menu = ctk.CTkOptionMenu(
            f_row,
            variable=self.inv_category_filter_var,
            values=cat_options,
            width=175,
            height=34,
            fg_color=NAVY,
            button_color=NAVY,
            button_hover_color=NAVY_HOVER,
            command=lambda _c: self.refresh_inventory()
        )
        cat_menu.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            f_row,
            text="Status:",
            text_color=TEXT,
            font=self.font_bold_12
        ).pack(side="left", padx=(0, 6))

        self.inv_status_filter_var = ctk.StringVar(value="All Statuses")
        status_menu = ctk.CTkOptionMenu(
            f_row,
            variable=self.inv_status_filter_var,
            values=["All Statuses", "In Stock", "Low Stock", "Out of Stock"],
            width=140,
            height=34,
            fg_color=BLUE,
            button_color=BLUE,
            button_hover_color=BLUE_HOVER,
            command=lambda _s: self.refresh_inventory()
        )
        status_menu.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            f_row,
            text="Sort By:",
            text_color=TEXT,
            font=self.font_bold_12
        ).pack(side="left", padx=(0, 6))

        self.inv_sort_var = ctk.StringVar(value="Newest First (ID ↓)")
        sort_menu = ctk.CTkOptionMenu(
            f_row,
            variable=self.inv_sort_var,
            values=[
                "Newest First (ID ↓)",
                "Product Name (A → Z)",
                "Quantity: Low to High",
                "Quantity: High to Low",
                "Unit Price: Low to High",
                "Unit Price: High to Low",
                "Stock Value: High to Low",
            ],
            width=185,
            height=34,
            fg_color=NAVY,
            button_color=NAVY,
            button_hover_color=NAVY_HOVER,
            command=lambda _o: self.refresh_inventory()
        )
        sort_menu.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_row,
            text="Reset Filters",
            width=100,
            height=34,
            fg_color=PAGE_BG,
            hover_color=BORDER,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
            font=self.font_bold_12,
            command=self._reset_inventory_filters
        ).pack(side="left")

        # Right side row action buttons (Edit Selected / Delete Selected)
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

        # ----------------------------------------------------
        # 3. TABLE PANEL + LIVE FILTER SUMMARY FOOTER
        # ----------------------------------------------------
        self.inventory_panel = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        self.inventory_panel.pack(fill="both", expand=True)

        self.inv_summary_label = ctk.CTkLabel(
            self.content,
            text="",
            text_color=MUTED,
            font=self.font_bold_12
        )
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
        query = self.search_var.get().strip()
        products = list(search_products(query) if query else get_products())

        if self.inv_category_filter_var:
            cat_filter = self.inv_category_filter_var.get()
            if cat_filter and cat_filter != "All Categories":
                products = [p for p in products if str(p[3]) == cat_filter]

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

    # ========================================================
    # INVENTORY TABLE (WITH STOCK VALUE COLUMN)
    # ========================================================
    def create_inventory_table(self, parent, products, height=13, include_total_value=True):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(14, 18))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        if include_total_value:
            columns = (
                "id",
                "sku",
                "name",
                "category",
                "quantity",
                "price",
                "total_value",
                "status"
            )
        else:
            columns = (
                "id",
                "sku",
                "name",
                "category",
                "quantity",
                "price",
                "status"
            )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            style="Inventory.Treeview",
            height=height
        )

        headings = {
            "id": "ID",
            "sku": "SKU",
            "name": "Product Name",
            "category": "Category",
            "quantity": "Quantity",
            "price": "Unit Price (₹)",
            "total_value": "Stock Value (₹)",
            "status": "Status"
        }
        widths = {
            "id": 50,
            "sku": 105,
            "name": 215,
            "category": 145,
            "quantity": 85,
            "price": 110,
            "total_value": 120,
            "status": 110
        }

        for column in columns:
            tree.heading(
                column,
                text=headings[column],
                command=lambda col=column, tr=tree: self._sort_treeview_by_column(tr, col, False)
            )
            tree.column(column, width=widths[column], anchor="w")

        tree.tag_configure("low", foreground=ORANGE)
        tree.tag_configure("out", foreground=RED)

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nswe")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._populate_tree(tree, products, include_total_value=include_total_value)
        return tree

    def _sort_treeview_by_column(self, tree, col, reverse=False):
        if tree is None or not tree.winfo_exists():
            return
        rows = [(tree.set(k, col), k) for k in tree.get_children("")]
        def parse_val(v):
            cleaned = str(v).replace("₹", "").replace(",", "").strip()
            try:
                return (0, float(cleaned))
            except ValueError:
                return (1, cleaned.lower())
        rows.sort(key=lambda item: parse_val(item[0]), reverse=reverse)
        for index, (_val, k) in enumerate(rows):
            tree.move(k, "", index)
        tree.heading(
            col,
            command=lambda c=col, tr=tree, rev=not reverse: self._sort_treeview_by_column(tr, c, rev)
        )

    def _populate_tree(self, tree, products, include_total_value=True):
        """Fast in-place population of a Treeview without recreating widgets."""
        if tree is None or not tree.winfo_exists():
            return
        for item in tree.get_children():
            tree.delete(item)
        for product in products:
            status_val = str(product[6]).lower() if len(product) > 6 else ""
            tags = ()
            if "out" in status_val:
                tags = ("out",)
            elif "low" in status_val:
                tags = ("low",)

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

    # ========================================================
    # REFRESH INVENTORY (IN-PLACE OPTIMIZED)
    # ========================================================
    def refresh_inventory(self):
        if not hasattr(self, "inventory_panel") or not self.inventory_panel.winfo_exists():
            return

        products = self._get_filtered_and_sorted_inventory()

        if hasattr(self, "inv_summary_label") and self.inv_summary_label.winfo_exists():
            total_units = sum(int(p[4]) for p in products)
            total_val = sum(int(p[4]) * float(p[5]) for p in products)
            self.inv_summary_label.configure(
                text=f"Showing {len(products)} products  •  Total Units: {total_units:,}  •  Filtered Stock Valuation: ₹{total_val:,.2f}"
            )

        if self.inventory_tree is not None and self.inventory_tree.winfo_exists():
            self._populate_tree(self.inventory_tree, products, include_total_value=True)
            return

        for widget in self.inventory_panel.winfo_children():
            widget.destroy()

        self.inventory_tree = self.create_inventory_table(
            self.inventory_panel,
            products,
            height=13,
            include_total_value=True
        )
        self.inventory_tree.bind("<Double-1>", self.edit_selected_product)
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)

    # ========================================================
    # DEBOUNCED SEARCH (WORKS SAFELY ACROSS PAGES)
    # ========================================================
    def _on_search_keyrelease(self, event=None):
        if self._search_after_id is not None:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:
                pass
        self._search_after_id = self.after(180, self.search_inventory)

    def search_inventory(self, event=None):
        self._search_after_id = None
        query = self.search_var.get().strip()

        if self.inventory_tree is not None and self.inventory_tree.winfo_exists():
            self.refresh_inventory()
        elif self.dashboard_tree is not None and self.dashboard_tree.winfo_exists():
            filtered = self._get_filtered_dashboard_products(query)
            self._populate_tree(self.dashboard_tree, filtered, include_total_value=True)

    # ========================================================
    # QUICK STOCK ADJUSTMENT MODAL
    # ========================================================
    def open_quick_stock_adjust(self):
        selected_values = None
        if self.inventory_tree is not None and self.inventory_tree.winfo_exists():
            sel = self.inventory_tree.selection()
            if sel:
                selected_values = self.inventory_tree.item(sel[0], "values")

        if not selected_values:
            messagebox.showinfo(
                "Select a Product",
                "Please select a product row in the Inventory table first to adjust its stock.",
                parent=self
            )
            return

        p_id = int(selected_values[0])
        sku = str(selected_values[1])
        name = str(selected_values[2])
        cat = str(selected_values[3])
        current_qty = int(selected_values[4])
        price = float(str(selected_values[5]).replace("₹", "").replace(",", ""))

        win = ctk.CTkToplevel(self)
        win.title(f"Quick Stock Adjust - {sku}")
        win.geometry("420x350")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="⚡ Quick Stock Adjustment",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT
        ).pack(pady=(22, 6))

        ctk.CTkLabel(
            win,
            text=f"{name} ({sku})\nCurrent Stock: {current_qty} units",
            text_color=MUTED,
            font=self.font_bold_12
        ).pack(pady=(0, 16))

        preset_frame = ctk.CTkFrame(win, fg_color="transparent")
        preset_frame.pack(fill="x", padx=28, pady=(0, 14))

        def apply_delta(delta):
            new_q = max(0, current_qty + delta)
            ok, msg = update_product(p_id, sku, name, cat, new_q, price)
            if ok:
                win.destroy()
                self.refresh_inventory()
                self.refresh_dashboard_if_needed()
            else:
                messagebox.showerror("Error", msg, parent=win)

        for label_txt, delta_val, col in (
            ("−5", -5, RED),
            ("−1", -1, ORANGE),
            ("+1", 1, BLUE),
            ("+5", 5, GREEN),
            ("+10", 10, GREEN),
            ("+25", 25, NAVY),
        ):
            ctk.CTkButton(
                preset_frame,
                text=label_txt,
                width=52,
                height=34,
                fg_color=col,
                command=lambda d=delta_val: apply_delta(d)
            ).pack(side="left", expand=True, padx=2)

        ctk.CTkLabel(
            win,
            text="Or set exact new stock quantity:",
            text_color=TEXT,
            font=self.font_bold_12
        ).pack(pady=(6, 4))

        exact_entry = ctk.CTkEntry(win, height=36, justify="center")
        exact_entry.pack(fill="x", padx=40, pady=(0, 16))
        exact_entry.insert(0, str(current_qty))

        def save_exact():
            try:
                new_q = int(exact_entry.get().strip())
                if new_q < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Enter a non-negative integer.", parent=win)
                return
            ok, msg = update_product(p_id, sku, name, cat, new_q, price)
            if ok:
                win.destroy()
                self.refresh_inventory()
                self.refresh_dashboard_if_needed()
            else:
                messagebox.showerror("Error", msg, parent=win)

        ctk.CTkButton(
            win,
            text="Save Exact Stock",
            height=40,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=save_exact
        ).pack(fill="x", padx=40)

    # ========================================================
    # ADD PRODUCT WINDOW (WITH AUTO-SKU GENERATOR)
    # ========================================================
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
        # SKU Row with Auto-Generate Button
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

    # ========================================================
    # EDIT PRODUCT (FIXED ROW CHECK & VALIDATION)
    # ========================================================
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

    # ========================================================
    # EDIT WINDOW
    # ========================================================
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

    # ========================================================
    # RIGHT CLICK MENU (WITH QUICK STOCK & POS CART ACTIONS)
    # ========================================================
    def show_context_menu(self, event):
        if self.inventory_tree is None or not self.inventory_tree.winfo_exists():
            return

        item = self.inventory_tree.identify_row(event.y)
        if not item:
            return

        self.inventory_tree.selection_set(item)
        values = self.inventory_tree.item(item, "values")

        context_menu = tk.Menu(
            self,
            tearoff=0,
            bg=WHITE,
            fg=TEXT,
            activebackground=BLUE,
            activeforeground=WHITE,
            font=("Segoe UI", 10)
        )
        context_menu.add_command(
            label="✏  Edit Product",
            command=self.edit_selected_product
        )
        context_menu.add_command(
            label="⚡  Quick Stock Adjust...",
            command=self.open_quick_stock_adjust
        )
        if values:
            prod_tuple = (
                int(values[0]),
                str(values[1]),
                str(values[2]),
                str(values[3]),
                int(values[4]),
                float(str(values[5]).replace("₹", "").replace(",", "")),
                str(values[-1]),
            )
            context_menu.add_command(
                label="➕  Quick Restock (+10 Units)",
                command=lambda p=prod_tuple: self._quick_restock_product(p, 10)
            )
            context_menu.add_command(
                label="🛒  Send to Billing Cart",
                command=lambda p=prod_tuple: self._send_product_tuple_to_pos_cart(p)
            )
        context_menu.add_separator()
        context_menu.add_command(
            label="🗑  Delete Product",
            foreground=RED,
            command=self.delete_selected_product
        )
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _send_product_tuple_to_pos_cart(self, prod_tuple):
        p_id, sku, name, cat, qty, price, status = prod_tuple
        if qty <= 0:
            messagebox.showwarning(
                "Out of Stock",
                f"'{name}' is Out of Stock. Restock it first before billing.",
                parent=self
            )
            return
        self._add_product_dict_to_cart({
            "id": p_id,
            "sku": sku,
            "name": name,
            "category": cat,
            "stock": qty,
            "price": price,
            "status": status
        })
        messagebox.showinfo(
            "Added to POS Cart",
            f"1 unit of '{name}' ({sku}) was added to the Billing Cart.",
            parent=self
        )

    # ========================================================
    # DELETE PRODUCT
    # ========================================================
    def delete_selected_product(self):
        if self.inventory_tree is None or not self.inventory_tree.winfo_exists():
            return

        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Select a Product",
                "Please select a product row first to delete.",
                parent=self
            )
            return

        values = self.inventory_tree.item(selected[0], "values")
        product_id = values[0]
        product_name = values[2]

        confirm = messagebox.askyesno(
            "Delete Product",
            f"Are you sure you want to delete:\n\n{product_name}?",
            parent=self
        )
        if not confirm:
            return

        success, message = delete_product(int(product_id))
        if success:
            messagebox.showinfo("Deleted", message)
            self.refresh_inventory()
            self.refresh_dashboard_if_needed()
        else:
            messagebox.showerror("Error", message)

    # ========================================================
    # IMPORT CSV
    # ========================================================
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select Inventory CSV",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return

        try:
            added, skipped, errors = import_products_from_csv(file_path)
            if self.current_page == "Inventory":
                self.show_inventory()
            else:
                self.refresh_dashboard_if_needed()

            if skipped == 0:
                messagebox.showinfo(
                    "Import Complete",
                    f"{added} products imported successfully."
                )
            else:
                error_text = "\n".join(errors[:10])
                if len(errors) > 10:
                    error_text += "\n\n...and more errors."
                messagebox.showwarning(
                    "Import Completed",
                    f"Products added: {added}\n"
                    f"Products skipped: {skipped}\n\n"
                    f"{error_text}"
                )
        except Exception as error:
            messagebox.showerror(
                "Import Error",
                f"Could not import CSV file.\n\n{error}"
            )

    # ========================================================
    # EXPORT CSV
    # ========================================================
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Inventory",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="inventory_export.csv"
        )
        if not file_path:
            return

        try:
            count = export_products_to_csv(file_path)
            messagebox.showinfo(
                "Export Complete",
                f"{count} products exported successfully.\n\nSaved to:\n{file_path}"
            )
        except Exception as error:
            messagebox.showerror(
                "Export Error",
                f"Could not export CSV.\n\n{error}"
            )

    # ========================================================
    # REFRESH DASHBOARD
    # ========================================================
    def refresh_dashboard_if_needed(self):
        if self.current_page == "Dashboard":
            self.show_dashboard()

    # ========================================================
    # REDESIGNED POS BILLING & INVOICING TERMINAL
    # ========================================================
    def show_billing(self):
        self._billing_products = []
        for p in get_products():
            self._billing_products.append({
                "id": int(p[0]),
                "sku": str(p[1]),
                "name": str(p[2]),
                "category": str(p[3]),
                "stock": int(p[4]),
                "price": float(p[5]),
                "status": str(p[6])
            })

        # 1. POS TERMINAL HEADER CARD
        pos_header_card = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        pos_header_card.pack(fill="x", pady=(0, 14))

        top_bar_row = ctk.CTkFrame(pos_header_card, fg_color="transparent")
        top_bar_row.pack(fill="x", padx=22, pady=(16, 10))

        brand_col = ctk.CTkFrame(top_bar_row, fg_color="transparent")
        brand_col.pack(side="left")

        title_line = ctk.CTkFrame(brand_col, fg_color="transparent")
        title_line.pack(anchor="w")

        store_title = self.app_settings.get("store_name", "IMABS")
        ctk.CTkLabel(
            title_line,
            text=f"🧾 {store_title} POS Terminal",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=BLUE
        ).pack(side="left")

        ctk.CTkLabel(
            title_line,
            text="   ● Status: Online",
            font=self.font_bold_12,
            text_color=GREEN
        ).pack(side="left", pady=(3, 0))

        self.invoice_no_var = ctk.StringVar(value=self._generate_invoice_number())
        meta_line = ctk.CTkFrame(brand_col, fg_color="transparent")
        meta_line.pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            meta_line,
            text="TXN: #",
            text_color=MUTED,
            font=self.font_bold_12
        ).pack(side="left")

        ctk.CTkLabel(
            meta_line,
            textvariable=self.invoice_no_var,
            text_color=TEXT,
            font=self.font_bold_12
        ).pack(side="left")

        ctk.CTkLabel(
            meta_line,
            text="   |   Shortcuts: F1 New  •  F2 Scan/Search  •  F4 Discount  •  F8 Reprint  •  F10 Checkout",
            text_color=MUTED,
            font=self.font_small_11
        ).pack(side="left")

        action_btns = ctk.CTkFrame(top_bar_row, fg_color="transparent")
        action_btns.pack(side="right")

        ctk.CTkButton(
            action_btns,
            text="⊕ New Transaction  [F1]",
            height=36,
            width=165,
            corner_radius=7,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            font=self.font_bold_12,
            command=self._start_new_transaction
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_btns,
            text="🔍 Product Search  [F2]",
            height=36,
            width=160,
            corner_radius=7,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=self.font_bold_12,
            command=self._shortcut_focus_scan_search
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_btns,
            text="📤 Export Invoices",
            height=36,
            width=135,
            corner_radius=7,
            fg_color=ORANGE,
            hover_color=ORANGE_HOVER,
            font=self.font_bold_12,
            command=self._export_invoices_csv
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_btns,
            text="🗑 Clear Cart",
            height=36,
            width=105,
            corner_radius=7,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            font=self.font_bold_12,
            command=self._clear_cart
        ).pack(side="left")

        cust_strip = ctk.CTkFrame(
            pos_header_card,
            fg_color=PAGE_BG,
            corner_radius=8
        )
        cust_strip.pack(fill="x", padx=22, pady=(2, 14))
        cust_strip.grid_columnconfigure(1, weight=2)
        cust_strip.grid_columnconfigure(3, weight=2)
        cust_strip.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(
            cust_strip,
            text="Customer:",
            text_color=TEXT,
            font=self.font_bold_12
        ).grid(row=0, column=0, padx=(14, 6), pady=8, sticky="w")

        self.cust_name_entry = ctk.CTkEntry(
            cust_strip,
            height=32,
            placeholder_text="Walk-in Customer / Enter Name",
            border_color=BORDER,
            fg_color=WHITE
        )
        self.cust_name_entry.grid(row=0, column=1, padx=(0, 14), pady=8, sticky="we")

        ctk.CTkLabel(
            cust_strip,
            text="Phone:",
            text_color=TEXT,
            font=self.font_bold_12
        ).grid(row=0, column=2, padx=(4, 6), pady=8, sticky="w")

        self.cust_phone_entry = ctk.CTkEntry(
            cust_strip,
            height=32,
            placeholder_text="+91 9876543210 (Optional)",
            border_color=BORDER,
            fg_color=WHITE
        )
        self.cust_phone_entry.grid(row=0, column=3, padx=(0, 14), pady=8, sticky="we")

        ctk.CTkLabel(
            cust_strip,
            text="Payment Mode:",
            text_color=TEXT,
            font=self.font_bold_12
        ).grid(row=0, column=4, padx=(4, 6), pady=8, sticky="w")

        self.payment_method_var = ctk.StringVar(value="Cash")
        self.payment_dropdown = ctk.CTkOptionMenu(
            cust_strip,
            variable=self.payment_method_var,
            values=["Cash", "UPI", "Card", "Bank Transfer"],
            height=32,
            fg_color=NAVY,
            button_color=NAVY,
            button_hover_color=NAVY_HOVER
        )
        self.payment_dropdown.grid(row=0, column=5, padx=(0, 14), pady=8, sticky="we")

        # 2. MAIN TWO-COLUMN POS WORKSPACE
        workspace = ctk.CTkFrame(self.content, fg_color="transparent")
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=7)
        workspace.grid_columnconfigure(1, weight=3)

        left_col = ctk.CTkFrame(workspace, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        scan_card = ctk.CTkFrame(
            left_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        scan_card.pack(fill="x", pady=(0, 14))

        scan_top_row = ctk.CTkFrame(scan_card, fg_color="transparent")
        scan_top_row.pack(fill="x", padx=20, pady=(14, 6))

        ctk.CTkLabel(
            scan_top_row,
            text="🔍 Scan Products / Quick Search",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            scan_top_row,
            text="Type SKU or Product Name  •  ↑/↓ Select  •  Press Enter ↵ to Add to Cart",
            font=self.font_small_11,
            text_color=MUTED
        ).pack(side="right")

        search_bar_container = ctk.CTkFrame(
            scan_card,
            fg_color=WHITE,
            corner_radius=8,
            border_width=2,
            border_color=BLUE
        )
        search_bar_container.pack(fill="x", padx=20, pady=(0, 10))
        search_bar_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_bar_container,
            text="🏷",
            font=ctk.CTkFont(size=16),
            text_color=BLUE
        ).grid(row=0, column=0, padx=(12, 4), pady=6)

        self.pos_search_var = ctk.StringVar()
        self.pos_search_entry = ctk.CTkEntry(
            search_bar_container,
            textvariable=self.pos_search_var,
            height=36,
            border_width=0,
            fg_color=WHITE,
            text_color=TEXT,
            font=self.font_regular_13,
            placeholder_text="Scan barcode, SKU, or enter product name... (e.g. SKU-1001, Mouse, Monitor)"
        )
        self.pos_search_entry.grid(row=0, column=1, sticky="we", padx=4, pady=4)

        ctk.CTkLabel(
            search_bar_container,
            text="Qty:",
            font=self.font_bold_12,
            text_color=MUTED
        ).grid(row=0, column=2, padx=(6, 4), pady=4)

        self.bill_qty_entry = ctk.CTkEntry(
            search_bar_container,
            width=52,
            height=30,
            border_width=1,
            border_color=BORDER,
            fg_color=PAGE_BG,
            justify="center",
            font=self.font_bold_12
        )
        self.bill_qty_entry.insert(0, "1")
        self.bill_qty_entry.grid(row=0, column=3, padx=(0, 8), pady=4)

        enter_badge_btn = ctk.CTkButton(
            search_bar_container,
            text="Enter ↵",
            width=76,
            height=30,
            corner_radius=6,
            fg_color=PAGE_BG,
            hover_color=BLUE,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
            font=self.font_bold_12,
            command=self._on_pos_search_enter
        )
        enter_badge_btn.grid(row=0, column=4, padx=(0, 8), pady=4)

        self.pos_search_entry.bind("<KeyRelease>", self._on_pos_search_keyrelease)
        self.pos_search_entry.bind("<Return>", self._on_pos_search_enter)
        self.pos_search_entry.bind("<Down>", self._on_pos_search_down)
        self.pos_search_entry.bind("<Up>", self._on_pos_search_up)
        self.bill_qty_entry.bind("<Return>", self._on_pos_search_enter)

        self.pos_suggestions_frame = ctk.CTkFrame(
            scan_card,
            fg_color=PAGE_BG,
            corner_radius=8
        )
        self.pos_suggestions_frame.pack(fill="x", padx=20, pady=(0, 14))

        cart_card = ctk.CTkFrame(
            left_col,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        cart_card.pack(fill="both", expand=True)

        cart_top_bar = ctk.CTkFrame(cart_card, fg_color="transparent")
        cart_top_bar.pack(fill="x", padx=20, pady=(16, 10))

        ctk.CTkLabel(
            cart_top_bar,
            text="🛒 Shopping Cart",
            font=self.font_section_title,
            text_color=TEXT
        ).pack(side="left")

        self.cart_badge_label = ctk.CTkLabel(
            cart_top_bar,
            text="0 Items",
            fg_color="#DBEAFE",
            text_color=BLUE,
            corner_radius=12,
            padx=12,
            pady=3,
            font=self.font_bold_12
        )
        self.cart_badge_label.pack(side="right")

        col_header = ctk.CTkFrame(
            cart_card,
            fg_color=PAGE_BG,
            corner_radius=6,
            height=34
        )
        col_header.pack(fill="x", padx=20, pady=(0, 6))
        self._configure_cart_grid_columns(col_header)

        headers = [
            (0, "PRODUCT DETAILS", "w"),
            (1, "PRICE", "e"),
            (2, "QTY", "center"),
            (3, "DISC.", "e"),
            (4, "TAX", "e"),
            (5, "TOTAL", "e"),
            (6, "ACTION", "center"),
        ]
        for col_idx, text_val, align in headers:
            ctk.CTkLabel(
                col_header,
                text=text_val,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=MUTED,
                anchor=align
            ).grid(row=0, column=col_idx, sticky="we", padx=8, pady=6)

        self.cart_rows_container = ctk.CTkScrollableFrame(
            cart_card,
            fg_color=WHITE,
            corner_radius=0,
            height=290
        )
        self.cart_rows_container.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.cart_rows_container.grid_columnconfigure(0, weight=1)

        # RIGHT COLUMN: CART SUMMARY PANEL
        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        summary_card = ctk.CTkFrame(
            right_col,
            fg_color=NAVY,
            corner_radius=12,
            border_width=1,
            border_color=NAVY_HOVER
        )
        summary_card.pack(fill="both", expand=True)

        sum_header = ctk.CTkFrame(summary_card, fg_color="transparent")
        sum_header.pack(fill="x", padx=22, pady=(20, 12))

        ctk.CTkLabel(
            sum_header,
            text="🧾 Cart Summary",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color=WHITE
        ).pack(side="left")

        tax_disc_box = ctk.CTkFrame(
            summary_card,
            fg_color=NAVY_HOVER,
            corner_radius=8
        )
        tax_disc_box.pack(fill="x", padx=22, pady=(0, 14))
        tax_disc_box.grid_columnconfigure(0, weight=1)
        tax_disc_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            tax_disc_box,
            text="Discount (%)  [F4]",
            text_color="#CBD5E1",
            font=self.font_bold_12,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 3))

        self.discount_var = ctk.StringVar(
            value=self.app_settings.get("default_discount_pct", "0")
        )
        self.discount_entry = ctk.CTkEntry(
            tax_disc_box,
            height=32,
            textvariable=self.discount_var,
            fg_color=WHITE,
            text_color=TEXT,
            border_color=BORDER
        )
        self.discount_entry.grid(row=1, column=0, sticky="we", padx=(12, 6), pady=(0, 10))
        self.discount_entry.bind("<KeyRelease>", lambda _e: self._refresh_cart_table())

        ctk.CTkLabel(
            tax_disc_box,
            text="Tax / GST (%)",
            text_color="#CBD5E1",
            font=self.font_bold_12,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(6, 12), pady=(10, 3))

        self.tax_var = ctk.StringVar(
            value=self.app_settings.get("default_tax_pct", "18")
        )
        self.tax_entry = ctk.CTkEntry(
            tax_disc_box,
            height=32,
            textvariable=self.tax_var,
            fg_color=WHITE,
            text_color=TEXT,
            border_color=BORDER
        )
        self.tax_entry.grid(row=1, column=1, sticky="we", padx=(6, 12), pady=(0, 10))
        self.tax_entry.bind("<KeyRelease>", lambda _e: self._refresh_cart_table())

        metrics_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=22, pady=(2, 8))

        self.lbl_items_count = self._create_pos_summary_row(
            metrics_frame, "Items Count:", "0 items (0 qty)", WHITE
        )
        self.lbl_subtotal = self._create_pos_summary_row(
            metrics_frame, "Subtotal:", "₹0.00", WHITE
        )
        self.lbl_discount = self._create_pos_summary_row(
            metrics_frame, "Total Discount:", "-₹0.00", "#FBBF24"
        )
        self.lbl_tax = self._create_pos_summary_row(
            metrics_frame, "Tax (GST):", "+₹0.00", "#34D399"
        )

        ctk.CTkFrame(
            summary_card,
            height=1,
            fg_color=NAVY_HOVER
        ).pack(fill="x", padx=22, pady=10)

        grand_row = ctk.CTkFrame(summary_card, fg_color="transparent")
        grand_row.pack(fill="x", padx=22, pady=(2, 16))

        tot_lbl_col = ctk.CTkFrame(grand_row, fg_color="transparent")
        tot_lbl_col.pack(side="left")
        ctk.CTkLabel(
            tot_lbl_col,
            text="Total\nAmount:",
            justify="left",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#CBD5E1"
        ).pack(anchor="w")

        self.lbl_grand_total = ctk.CTkLabel(
            grand_row,
            text="₹0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=WHITE
        )
        self.lbl_grand_total.pack(side="right")

        btn_stack = ctk.CTkFrame(summary_card, fg_color="transparent")
        btn_stack.pack(fill="x", padx=22, pady=(4, 10))

        self.checkout_btn = ctk.CTkButton(
            btn_stack,
            text="🛍  Checkout (₹0.00)  [F10]",
            height=46,
            corner_radius=8,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._finalize_invoice
        )
        self.checkout_btn.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_stack,
            text="🏷  Quick Discount / Coupon  [F4]",
            height=38,
            corner_radius=8,
            fg_color=ORANGE,
            hover_color=ORANGE_HOVER,
            font=self.font_bold_12,
            command=self._open_quick_discount_dialog
        ).pack(fill="x", pady=(0, 8))

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

        # 3. BOTTOM SECTION: RECENT INVOICES HISTORY
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
        self.invoices_tree.grid(row=0, column=0, sticky="nswe")
        inv_scroll.grid(row=0, column=1, sticky="ns")
        self.invoices_tree.bind("<Double-1>", self._on_invoice_history_double_click)
        self.invoices_tree.bind("<Return>", self._on_invoice_history_double_click)

        self._update_pos_search_results()
        self._refresh_cart_table()
        self._refresh_invoice_history_table()

    def _configure_cart_grid_columns(self, frame):
        frame.grid_columnconfigure(0, weight=4, minsize=190)
        frame.grid_columnconfigure(1, weight=1, minsize=75)
        frame.grid_columnconfigure(2, weight=2, minsize=105)
        frame.grid_columnconfigure(3, weight=1, minsize=75)
        frame.grid_columnconfigure(4, weight=1, minsize=75)
        frame.grid_columnconfigure(5, weight=1, minsize=90)
        frame.grid_columnconfigure(6, weight=1, minsize=50)

    def _create_pos_summary_row(self, parent, label_text, default_val, val_color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(
            row,
            text=label_text,
            text_color="#CBD5E1",
            font=self.font_regular_13
        ).pack(side="left")
        val_lbl = ctk.CTkLabel(
            row,
            text=default_val,
            text_color=val_color,
            font=self.font_bold_14
        )
        val_lbl.pack(side="right")
        return val_lbl

    # ========================================================
    # POS LIVE SEARCH & BARCODE/SKU ADD ENGINE
    # ========================================================
    def _on_pos_search_keyrelease(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return", "Escape"):
            return
        if self._pos_search_after_id is not None:
            try:
                self.after_cancel(self._pos_search_after_id)
            except Exception:
                pass
        self._pos_search_after_id = self.after(100, self._update_pos_search_results)

    def _on_pos_search_down(self, event=None):
        if not self._pos_matched_products:
            return "break"
        self._pos_selected_match_idx = (
            (self._pos_selected_match_idx + 1) % len(self._pos_matched_products)
        )
        self._render_pos_suggestion_rows()
        return "break"

    def _on_pos_search_up(self, event=None):
        if not self._pos_matched_products:
            return "break"
        self._pos_selected_match_idx = (
            (self._pos_selected_match_idx - 1) % len(self._pos_matched_products)
        )
        self._render_pos_suggestion_rows()
        return "break"

    def _on_pos_search_enter(self, event=None):
        if not self._pos_matched_products:
            messagebox.showwarning(
                "No Matching Product",
                "No matching product found for your search query.",
                parent=self
            )
            return "break"

        idx = min(self._pos_selected_match_idx, len(self._pos_matched_products) - 1)
        chosen_prod = self._pos_matched_products[max(0, idx)]
        self._add_product_dict_to_cart(chosen_prod)
        self.pos_search_var.set("")
        self._pos_selected_match_idx = 0
        self._update_pos_search_results()
        if hasattr(self, "pos_search_entry") and self.pos_search_entry.winfo_exists():
            self.pos_search_entry.focus_set()
        return "break"

    def _update_pos_search_results(self):
        self._pos_search_after_id = None
        if not hasattr(self, "pos_suggestions_frame") or not self.pos_suggestions_frame.winfo_exists():
            return

        query = self.pos_search_var.get().strip().lower()
        if not query:
            in_stock_prods = [p for p in self._billing_products if p["stock"] > 0]
            self._pos_matched_products = in_stock_prods[:4]
        else:
            exact_sku = []
            partial = []
            for p in self._billing_products:
                sku_l = p["sku"].lower()
                name_l = p["name"].lower()
                cat_l = p["category"].lower()
                if sku_l == query:
                    exact_sku.append(p)
                elif query in sku_l or query in name_l or query in cat_l:
                    partial.append(p)
            self._pos_matched_products = (exact_sku + partial)[:5]

        self._pos_selected_match_idx = 0
        self._render_pos_suggestion_rows()

    def _render_pos_suggestion_rows(self):
        if not hasattr(self, "pos_suggestions_frame") or not self.pos_suggestions_frame.winfo_exists():
            return

        for w in self.pos_suggestions_frame.winfo_children():
            w.destroy()

        if not self._billing_products:
            ctk.CTkLabel(
                self.pos_suggestions_frame,
                text="No products in inventory yet. Add or Import CSV on the Inventory page.",
                text_color=MUTED,
                font=self.font_regular_12
            ).pack(padx=12, pady=8)
            return

        if not self._pos_matched_products:
            ctk.CTkLabel(
                self.pos_suggestions_frame,
                text="No matching products found. Try searching a different SKU, name, or category.",
                text_color=RED,
                font=self.font_regular_12
            ).pack(padx=12, pady=8)
            return

        for idx, prod in enumerate(self._pos_matched_products):
            is_selected = (idx == self._pos_selected_match_idx)
            row_bg = "#DBEAFE" if is_selected else WHITE
            border_c = BLUE if is_selected else BORDER

            item_row = ctk.CTkFrame(
                self.pos_suggestions_frame,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=border_c
            )
            item_row.pack(fill="x", padx=8, pady=3)

            left_info = ctk.CTkFrame(item_row, fg_color="transparent")
            left_info.pack(side="left", fill="x", expand=True, padx=10, pady=5)

            sku_badge = ctk.CTkLabel(
                left_info,
                text=prod["sku"],
                fg_color=NAVY if is_selected else PAGE_BG,
                text_color=WHITE if is_selected else TEXT,
                corner_radius=4,
                padx=7,
                pady=1,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            sku_badge.pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                left_info,
                text=prod["name"],
                text_color=TEXT,
                font=self.font_bold_12
            ).pack(side="left")

            ctk.CTkLabel(
                left_info,
                text=f"  ({prod['category']})",
                text_color=MUTED,
                font=self.font_small_11
            ).pack(side="left")

            right_info = ctk.CTkFrame(item_row, fg_color="transparent")
            right_info.pack(side="right", padx=8, pady=4)

            stock_color = GREEN if prod["stock"] > 10 else (ORANGE if prod["stock"] > 0 else RED)
            stock_text = f"Stock: {prod['stock']}" if prod["stock"] > 0 else "Out of Stock"
            ctk.CTkLabel(
                right_info,
                text=stock_text,
                text_color=stock_color,
                font=self.font_bold_12
            ).pack(side="left", padx=(0, 12))

            ctk.CTkLabel(
                right_info,
                text=f"₹{prod['price']:,.2f}",
                text_color=TEXT,
                font=self.font_bold_12
            ).pack(side="left", padx=(0, 10))

            add_btn = ctk.CTkButton(
                right_info,
                text="+ Add" if prod["stock"] > 0 else "No Stock",
                width=68,
                height=26,
                corner_radius=5,
                fg_color=BLUE if prod["stock"] > 0 else GRAY,
                hover_color=BLUE_HOVER if prod["stock"] > 0 else GRAY,
                state="normal" if prod["stock"] > 0 else "disabled",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda p=prod: self._add_product_dict_to_cart(p)
            )
            add_btn.pack(side="left")

    def _add_product_dict_to_cart(self, prod):
        if prod["stock"] <= 0:
            messagebox.showwarning(
                "Out of Stock",
                f"'{prod['name']}' ({prod['sku']}) is currently Out of Stock.",
                parent=self
            )
            return

        qty = 1
        if hasattr(self, "bill_qty_entry") and self.bill_qty_entry.winfo_exists():
            qty_text = self.bill_qty_entry.get().strip()
            try:
                qty = int(qty_text)
                if qty <= 0:
                    qty = 1
            except ValueError:
                qty = 1

        existing_item = next(
            (item for item in self.cart_items if item["id"] == prod["id"]),
            None
        )
        current_in_cart = existing_item["qty"] if existing_item else 0

        if current_in_cart + qty > prod["stock"]:
            messagebox.showwarning(
                "Insufficient Stock",
                f"Cannot add {qty} units of '{prod['name']}'.\n"
                f"Available stock: {prod['stock']} (Already in cart: {current_in_cart}).",
                parent=self
            )
            return

        if existing_item:
            existing_item["qty"] += qty
            existing_item["total"] = existing_item["qty"] * existing_item["price"]
        else:
            self.cart_items.append({
                "id": prod["id"],
                "sku": prod["sku"],
                "name": prod["name"],
                "category": prod["category"],
                "stock": prod["stock"],
                "qty": qty,
                "price": prod["price"],
                "total": qty * prod["price"]
            })

        if hasattr(self, "bill_qty_entry") and self.bill_qty_entry.winfo_exists():
            self.bill_qty_entry.delete(0, "end")
            self.bill_qty_entry.insert(0, "1")

        self._refresh_cart_table()

    # ========================================================
    # INTERACTIVE POS SHOPPING CART ROWS (- / + STEPPER & DELETE)
    # ========================================================
    def _change_cart_item_qty(self, product_id, delta):
        target = next((item for item in self.cart_items if item["id"] == product_id), None)
        if not target:
            return
        new_qty = target["qty"] + delta
        if new_qty <= 0:
            self.cart_items = [item for item in self.cart_items if item["id"] != product_id]
        elif new_qty > target["stock"]:
            messagebox.showwarning(
                "Stock Limit Reached",
                f"Only {target['stock']} units of '{target['name']}' available in stock.",
                parent=self
            )
            return
        else:
            target["qty"] = new_qty
            target["total"] = target["qty"] * target["price"]
        self._refresh_cart_table()

    def _remove_cart_item_by_id(self, product_id):
        self.cart_items = [item for item in self.cart_items if item["id"] != product_id]
        self._refresh_cart_table()

    def _clear_cart(self):
        self.cart_items.clear()
        self._refresh_cart_table()

    def _start_new_transaction(self):
        self.cart_items.clear()
        if hasattr(self, "cust_name_entry") and self.cust_name_entry.winfo_exists():
            self.cust_name_entry.delete(0, "end")
        if hasattr(self, "cust_phone_entry") and self.cust_phone_entry.winfo_exists():
            self.cust_phone_entry.delete(0, "end")
        if hasattr(self, "discount_var"):
            self.discount_var.set(self.app_settings.get("default_discount_pct", "0"))
        if hasattr(self, "invoice_no_var"):
            self.invoice_no_var.set(self._generate_invoice_number())
        self._refresh_cart_table()
        self._shortcut_focus_scan_search()

    def _refresh_cart_table(self):
        if not hasattr(self, "cart_rows_container") or not self.cart_rows_container.winfo_exists():
            return

        for w in self.cart_rows_container.winfo_children():
            w.destroy()

        b = self._calculate_bill_breakdown()
        disc_pct = b["disc_pct"]
        tax_pct = b["tax_pct"]

        if hasattr(self, "cart_badge_label") and self.cart_badge_label.winfo_exists():
            self.cart_badge_label.configure(
                text=f"{len(self.cart_items)} Items ({b['total_qty']} qty)"
            )

        if not self.cart_items:
            empty_box = ctk.CTkFrame(self.cart_rows_container, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=55)
            ctk.CTkLabel(
                empty_box,
                text="🛒 Your shopping cart is empty",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=MUTED
            ).pack()
            ctk.CTkLabel(
                empty_box,
                text="Scan a SKU/barcode above, press Enter in the search box, or click '+ Add' on any product.",
                font=self.font_regular_12,
                text_color=MUTED
            ).pack(pady=(4, 0))
            self._update_cart_totals()
            return

        for item in self.cart_items:
            line_sub = item["qty"] * item["price"]
            line_disc = line_sub * (disc_pct / 100.0)
            line_taxable = max(0.0, line_sub - line_disc)
            line_tax = line_taxable * (tax_pct / 100.0)
            line_final = line_taxable + line_tax

            row_card = ctk.CTkFrame(
                self.cart_rows_container,
                fg_color=WHITE,
                corner_radius=6,
                border_width=1,
                border_color=BORDER
            )
            row_card.pack(fill="x", padx=4, pady=4)
            self._configure_cart_grid_columns(row_card)

            details_box = ctk.CTkFrame(row_card, fg_color="transparent")
            details_box.grid(row=0, column=0, sticky="w", padx=10, pady=8)

            ctk.CTkLabel(
                details_box,
                text=item["name"],
                font=self.font_bold_12,
                text_color=TEXT,
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                details_box,
                text=f"SKU: {item['sku']}  |  {item['category']}  |  Stock: {item['stock']}",
                font=self.font_small_11,
                text_color=MUTED,
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                row_card,
                text=f"₹{item['price']:,.2f}",
                font=self.font_regular_12,
                text_color=TEXT,
                anchor="e"
            ).grid(row=0, column=1, sticky="we", padx=8)

            stepper = ctk.CTkFrame(
                row_card,
                fg_color=PAGE_BG,
                corner_radius=6,
                border_width=1,
                border_color=BORDER
            )
            stepper.grid(row=0, column=2, padx=8, pady=8)

            ctk.CTkButton(
                stepper,
                text="−",
                width=26,
                height=24,
                corner_radius=4,
                fg_color="transparent",
                hover_color=BORDER,
                text_color=TEXT,
                font=self.font_bold_14,
                command=lambda pid=item["id"]: self._change_cart_item_qty(pid, -1)
            ).pack(side="left", padx=2, pady=2)

            ctk.CTkLabel(
                stepper,
                text=str(item["qty"]),
                width=28,
                font=self.font_bold_12,
                text_color=TEXT
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                stepper,
                text="+",
                width=26,
                height=24,
                corner_radius=4,
                fg_color="transparent",
                hover_color=BORDER,
                text_color=TEXT,
                font=self.font_bold_14,
                command=lambda pid=item["id"]: self._change_cart_item_qty(pid, 1)
            ).pack(side="left", padx=2, pady=2)

            disc_box = ctk.CTkFrame(row_card, fg_color="transparent")
            disc_box.grid(row=0, column=3, sticky="e", padx=8)
            if disc_pct > 0:
                ctk.CTkLabel(
                    disc_box,
                    text=f"-₹{line_disc:,.2f}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=ORANGE
                ).pack(anchor="e")
                ctk.CTkLabel(
                    disc_box,
                    text=f"{disc_pct:.0f}% OFF",
                    font=ctk.CTkFont(size=10),
                    text_color=MUTED
                ).pack(anchor="e")
            else:
                ctk.CTkLabel(
                    disc_box,
                    text="—",
                    font=self.font_regular_12,
                    text_color=MUTED
                ).pack(anchor="e")

            tax_box = ctk.CTkFrame(row_card, fg_color="transparent")
            tax_box.grid(row=0, column=4, sticky="e", padx=8)
            ctk.CTkLabel(
                tax_box,
                text=f"+₹{line_tax:,.2f}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=GREEN
            ).pack(anchor="e")
            ctk.CTkLabel(
                tax_box,
                text=f"{tax_pct:.0f}% GST",
                font=ctk.CTkFont(size=10),
                text_color=MUTED
            ).pack(anchor="e")

            ctk.CTkLabel(
                row_card,
                text=f"₹{line_final:,.2f}",
                font=self.font_bold_12,
                text_color=TEXT,
                anchor="e"
            ).grid(row=0, column=5, sticky="we", padx=8)

            ctk.CTkButton(
                row_card,
                text="🗑",
                width=32,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#FEE2E2",
                text_color=RED,
                font=ctk.CTkFont(size=14),
                command=lambda pid=item["id"]: self._remove_cart_item_by_id(pid)
            ).grid(row=0, column=6, padx=6)

        self._update_cart_totals()

    def _calculate_bill_breakdown(self):
        subtotal = sum(item["qty"] * item["price"] for item in self.cart_items)
        total_qty = sum(item["qty"] for item in self.cart_items)

        try:
            disc_pct = float(
                (self.discount_var.get().strip() if hasattr(self, "discount_var") else "0") or 0.0
            )
            disc_pct = max(0.0, min(100.0, disc_pct))
        except Exception:
            disc_pct = 0.0

        try:
            tax_pct = float(
                (self.tax_var.get().strip() if hasattr(self, "tax_var") else "18") or 0.0
            )
            tax_pct = max(0.0, tax_pct)
        except Exception:
            tax_pct = 0.0

        disc_amount = subtotal * (disc_pct / 100.0)
        taxable_amount = max(0.0, subtotal - disc_amount)
        tax_amount = taxable_amount * (tax_pct / 100.0)
        grand_total = taxable_amount + tax_amount

        return {
            "total_qty": total_qty,
            "subtotal": subtotal,
            "disc_pct": disc_pct,
            "disc_amount": disc_amount,
            "tax_pct": tax_pct,
            "tax_amount": tax_amount,
            "grand_total": grand_total
        }

    def _update_cart_totals(self):
        b = self._calculate_bill_breakdown()
        if hasattr(self, "lbl_items_count") and self.lbl_items_count.winfo_exists():
            self.lbl_items_count.configure(
                text=f"{len(self.cart_items)} items ({b['total_qty']} qty)"
            )
            self.lbl_subtotal.configure(text=f"₹{b['subtotal']:,.2f}")
            self.lbl_discount.configure(
                text=f"-₹{b['disc_amount']:,.2f} ({b['disc_pct']:.1f}%)"
            )
            self.lbl_tax.configure(
                text=f"+₹{b['tax_amount']:,.2f} ({b['tax_pct']:.1f}%)"
            )
            self.lbl_grand_total.configure(text=f"₹{b['grand_total']:,.2f}")
        if hasattr(self, "checkout_btn") and self.checkout_btn.winfo_exists():
            self.checkout_btn.configure(
                text=f"🛍  Checkout (₹{b['grand_total']:,.2f})  [F10]"
            )

    def _open_quick_discount_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Apply Discount / Coupon")
        win.geometry("360x260")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Apply Discount (%)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            win,
            text="Select a preset coupon or enter a custom discount:",
            text_color=MUTED,
            font=self.font_regular_12
        ).pack(pady=(0, 12))

        preset_row = ctk.CTkFrame(win, fg_color="transparent")
        preset_row.pack(fill="x", padx=24, pady=(0, 14))

        def apply_pct(val):
            self.discount_var.set(str(val))
            self._refresh_cart_table()
            win.destroy()

        for pct in (0, 5, 10, 15, 20):
            ctk.CTkButton(
                preset_row,
                text=f"{pct}%",
                width=54,
                height=34,
                fg_color=BLUE if pct > 0 else GRAY,
                hover_color=BLUE_HOVER if pct > 0 else GRAY_HOVER,
                command=lambda v=pct: apply_pct(v)
            ).pack(side="left", expand=True, padx=3)

        custom_entry = ctk.CTkEntry(
            win,
            height=36,
            placeholder_text="Custom Discount % (e.g. 7.5)"
        )
        custom_entry.pack(fill="x", padx=28, pady=(0, 14))
        custom_entry.insert(0, self.discount_var.get())
        custom_entry.focus_set()

        def apply_custom(event=None):
            val_str = custom_entry.get().strip()
            try:
                val = max(0.0, min(100.0, float(val_str)))
                apply_pct(val)
            except ValueError:
                messagebox.showerror("Invalid Discount", "Enter a number between 0 and 100.", parent=win)

        custom_entry.bind("<Return>", apply_custom)
        ctk.CTkButton(
            win,
            text="Apply Discount",
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            command=apply_custom
        ).pack(fill="x", padx=28)

    def _reprint_last_invoice(self):
        invoices = self._fetch_recent_invoices(limit=1)
        if not invoices:
            messagebox.showinfo(
                "No Invoices Found",
                "No completed invoices are available to reprint yet.",
                parent=self
            )
            return
        target = invoices[0]
        raw_items = self._fetch_invoice_items(int(target[0]))
        items_list = [
            {
                "sku": r[0],
                "name": r[1],
                "qty": r[2],
                "price": float(r[3]),
                "total": float(r[4])
            }
            for r in raw_items
        ]
        receipt_data = {
            "invoice_no": target[1],
            "created_at": target[2],
            "customer_name": target[3],
            "customer_phone": target[4],
            "payment_method": target[5],
            "items": items_list,
            "breakdown": {
                "subtotal": float(target[7]),
                "disc_pct": float(target[8]),
                "disc_amount": float(target[9]),
                "tax_pct": float(target[10]),
                "tax_amount": float(target[11]),
                "grand_total": float(target[12])
            }
        }
        self._show_receipt_window(receipt_data)

    def _show_pos_shortcuts_modal(self):
        win = ctk.CTkToplevel(self)
        win.title("POS Keyboard Shortcuts & Help")
        win.geometry("480x420")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="⌨ POS Terminal Keyboard Shortcuts",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT
        ).pack(pady=(22, 6))

        ctk.CTkLabel(
            win,
            text="Speed up billing and checkout using these keyboard controls:",
            text_color=MUTED,
            font=self.font_regular_12
        ).pack(pady=(0, 14))

        shortcuts = [
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
        ]

        list_frame = ctk.CTkFrame(
            win,
            fg_color=WHITE,
            corner_radius=8,
            border_width=1,
            border_color=BORDER
        )
        list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        for key_name, desc in shortcuts:
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(
                row,
                text=key_name,
                width=110,
                fg_color=PAGE_BG,
                text_color=NAVY,
                corner_radius=5,
                font=self.font_bold_12
            ).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                row,
                text=desc,
                text_color=TEXT,
                font=self.font_regular_12,
                anchor="w"
            ).pack(side="left", fill="x")

        ctk.CTkButton(
            win,
            text="Got It",
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            command=win.destroy
        ).pack(fill="x", padx=24, pady=(0, 18))

    def _finalize_invoice(self):
        if not self.cart_items:
            messagebox.showwarning(
                "Empty Cart",
                "Please add at least one product to the cart before generating an invoice.",
                parent=self
            )
            return

        customer_name = self.cust_name_entry.get().strip() or "Walk-in Customer"
        customer_phone = self.cust_phone_entry.get().strip()
        payment_method = self.payment_method_var.get()
        invoice_no = self.invoice_no_var.get()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        b = self._calculate_bill_breakdown()

        for item in self.cart_items:
            new_qty = max(0, item["stock"] - item["qty"])
            ok, msg = update_product(
                item["id"],
                item["sku"],
                item["name"],
                item["category"],
                new_qty,
                item["price"]
            )
            if not ok:
                messagebox.showerror(
                    "Stock Update Error",
                    f"Could not update stock for {item['name']}:\n{msg}",
                    parent=self
                )
                return

        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO invoices (
                        invoice_no, customer_name, customer_phone, payment_method,
                        subtotal, discount_pct, discount_amount, tax_pct, tax_amount,
                        grand_total, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_no,
                        customer_name,
                        customer_phone,
                        payment_method,
                        b["subtotal"],
                        b["disc_pct"],
                        b["disc_amount"],
                        b["tax_pct"],
                        b["tax_amount"],
                        b["grand_total"],
                        created_at
                    )
                )
                invoice_id = cur.lastrowid
                for item in self.cart_items:
                    cur.execute(
                        """
                        INSERT INTO invoice_items (
                            invoice_id, product_id, sku, product_name,
                            quantity, unit_price, line_total
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            invoice_id,
                            item["id"],
                            item["sku"],
                            item["name"],
                            item["qty"],
                            item["price"],
                            item["qty"] * item["price"]
                        )
                    )
                conn.commit()
        except Exception as exc:
            messagebox.showerror(
                "Invoice Error",
                f"Stock was updated, but saving invoice history failed:\n{exc}",
                parent=self
            )
            return

        receipt_data = {
            "invoice_no": invoice_no,
            "created_at": created_at,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "payment_method": payment_method,
            "items": list(self.cart_items),
            "breakdown": b
        }

        self.cart_items.clear()
        self.show_billing()
        self._show_receipt_window(receipt_data)

    def _refresh_invoice_history_table(self):
        if not hasattr(self, "invoices_tree") or not self.invoices_tree.winfo_exists():
            return
        for row in self.invoices_tree.get_children():
            self.invoices_tree.delete(row)

        invoices = self._fetch_recent_invoices()
        for inv in invoices:
            self.invoices_tree.insert(
                "",
                "end",
                values=(
                    inv[0],
                    inv[1],
                    inv[2],
                    inv[3],
                    inv[4] or "-",
                    inv[5],
                    inv[6],
                    f"{float(inv[12]):,.2f}"
                )
            )

    def _on_invoice_history_double_click(self, event=None):
        if not hasattr(self, "invoices_tree") or not self.invoices_tree.winfo_exists():
            return
        if event and hasattr(event, "y") and event.y:
            clicked = self.invoices_tree.identify_row(event.y)
            if not clicked:
                return
        selected = self.invoices_tree.selection()
        if not selected:
            return
        values = self.invoices_tree.item(selected[0], "values")
        if not values:
            return

        inv_id = int(values[0])
        invoices = self._fetch_recent_invoices(limit=200)
        target = next((row for row in invoices if int(row[0]) == inv_id), None)
        if not target:
            return

        raw_items = self._fetch_invoice_items(inv_id)
        items_list = [
            {
                "sku": r[0],
                "name": r[1],
                "qty": r[2],
                "price": float(r[3]),
                "total": float(r[4])
            }
            for r in raw_items
        ]
        receipt_data = {
            "invoice_no": target[1],
            "created_at": target[2],
            "customer_name": target[3],
            "customer_phone": target[4],
            "payment_method": target[5],
            "items": items_list,
            "breakdown": {
                "subtotal": float(target[7]),
                "disc_pct": float(target[8]),
                "disc_amount": float(target[9]),
                "tax_pct": float(target[10]),
                "tax_amount": float(target[11]),
                "grand_total": float(target[12])
            }
        }
        self._show_receipt_window(receipt_data)

    def _format_receipt_text(self, data):
        b = data["breakdown"]
        store_name = self.app_settings.get("store_name", "IMABS")
        store_tagline = self.app_settings.get("store_tagline", "Inventory & Billing System")
        store_address = self.app_settings.get("store_address", "New Delhi, India")
        store_contact = self.app_settings.get("store_contact", "")

        lines = [
            "=" * 56,
            f"{store_name.upper()} - {store_tagline.upper()}".center(56),
            f"{store_address}".center(56),
        ]
        if store_contact:
            lines.append(f"{store_contact}".center(56))
        lines.extend([
            "=" * 56,
            f"Invoice No : {data['invoice_no']}",
            f"Date       : {data['created_at']}",
            f"Customer   : {data['customer_name']}",
            f"Phone      : {data['customer_phone'] or 'N/A'}",
            f"Payment    : {data['payment_method']}",
            "-" * 56,
            f"{'SKU':<10} {'Item':<20} {'Qty':>5} {'Price':>9} {'Total':>9}",
            "-" * 56,
        ])
        for item in data["items"]:
            name_short = item["name"][:19]
            sku_short = str(item["sku"])[:9]
            line_tot = item.get("total", item["qty"] * item["price"])
            lines.append(
                f"{sku_short:<10} {name_short:<20} {item['qty']:>5} "
                f"{item['price']:>9.2f} {line_tot:>9.2f}"
            )
        disc_label = f"Discount ({b['disc_pct']:.1f}%):"
        tax_label = f"Tax / GST ({b['tax_pct']:.1f}%):"
        lines.extend([
            "-" * 56,
            f"{'Subtotal:':<40} ₹{b['subtotal']:>12,.2f}",
            f"{disc_label:<40} -₹{b['disc_amount']:>11,.2f}",
            f"{tax_label:<40} +₹{b['tax_amount']:>11,.2f}",
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

        ctk.CTkLabel(
            win,
            text=f"Invoice {receipt_data['invoice_no']}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT
        ).pack(pady=(20, 10))

        receipt_text = self._format_receipt_text(receipt_data)

        textbox = ctk.CTkTextbox(
            win,
            width=480,
            height=430,
            font=ctk.CTkFont(family="Courier New", size=12),
            fg_color=WHITE,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER
        )
        textbox.pack(padx=25, pady=(5, 15))
        textbox.insert("1.0", receipt_text)
        textbox.configure(state="disabled")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(0, 20))

        def save_txt_receipt():
            path = filedialog.asksaveasfilename(
                parent=win,
                title="Save Invoice Receipt",
                defaultextension=".txt",
                initialfile=f"{receipt_data['invoice_no']}.txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(receipt_text)
                messagebox.showinfo(
                    "Saved",
                    f"Receipt saved to:\n{path}",
                    parent=win
                )

        ctk.CTkButton(
            btn_row,
            text="💾 Save Receipt (.txt)",
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            height=40,
            command=save_txt_receipt
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Close",
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            height=40,
            command=win.destroy
        ).pack(side="right", expand=True, fill="x", padx=(8, 0))

    def _export_invoices_csv(self):
        invoices = self._fetch_recent_invoices(limit=5000)
        if not invoices:
            messagebox.showinfo(
                "No Invoices",
                "There are no invoices to export yet.",
                parent=self
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Invoices CSV",
            defaultextension=".csv",
            initialfile="invoices_export.csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Invoice No", "Created At", "Customer Name",
                    "Customer Phone", "Payment Method", "Item Count",
                    "Subtotal", "Discount %", "Discount Amount",
                    "Tax %", "Tax Amount", "Grand Total"
                ])
                writer.writerows(invoices)
            messagebox.showinfo(
                "Export Complete",
                f"{len(invoices)} invoices exported to:\n{file_path}",
                parent=self
            )
        except Exception as exc:
            messagebox.showerror(
                "Export Error",
                f"Failed to export invoices:\n{exc}",
                parent=self
            )

    # ========================================================
    # REPORTS (REDESIGNED EXECUTIVE ANALYTICS DASHBOARD)
    # ========================================================
    @staticmethod
    def _format_inr_compact(value: float) -> str:
        """Format currency values compactly (e.g., ₹1.42L, ₹56.9K, ₹850)."""
        if value >= 100000:
            return f"₹{value / 100000:.2f}L"
        if value >= 1000:
            return f"₹{value / 1000:.1f}K"
        return f"₹{value:.0f}"

    def show_reports(self):
        self.clear_content()

        products = get_products()
        stats = get_dashboard_stats()

        category_quantity = defaultdict(int)
        category_value = defaultdict(float)
        category_sku_count = defaultdict(int)
        stock_status = {"In Stock": 0, "Low Stock": 0, "Out of Stock": 0}
        restock_items = []
        total_units = 0

        for product in products:
            p_id, sku, name, category, quantity, price, status = (
                product[0],
                str(product[1]),
                str(product[2]),
                str(product[3]),
                int(product[4]),
                float(product[5]),
                str(product[6]),
            )
            total_units += quantity
            category_quantity[category] += quantity
            category_value[category] += quantity * price
            category_sku_count[category] += 1
            stock_status[status] = stock_status.get(status, 0) + 1

            if quantity <= 10 or "low" in status.lower() or "out" in status.lower():
                restock_items.append((sku, name, category, quantity, price, status))

        restock_items.sort(key=lambda x: (x[3], x[1]))

        total_categories = len(category_sku_count)
        total_stock_val = float(stats.get("total_value", 0.0))

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Inventory Analytics & Reports",
            font=self.font_page_title,
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text=(
                f"Executive breakdown across {total_categories} categories and "
                f"{total_units:,} total units in stock"
            ),
            font=self.font_regular_13,
            text_color=MUTED
        ).pack(anchor="w", pady=(2, 0))

        controls_frame = ctk.CTkFrame(header, fg_color="transparent")
        controls_frame.pack(side="right", pady=5)

        if self.report_top_n_var is None:
            self.report_top_n_var = ctk.StringVar(value="Top 8 Categories")

        ctk.CTkLabel(
            controls_frame,
            text="Chart View:",
            text_color=MUTED,
            font=self.font_regular_13
        ).pack(side="left", padx=(0, 8))

        top_n_menu = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.report_top_n_var,
            values=["Top 5 Categories", "Top 8 Categories", "Top 10 Categories", "Top 12 Categories"],
            width=155,
            height=38,
            fg_color=NAVY,
            button_color=NAVY,
            button_hover_color=NAVY_HOVER,
            command=lambda _choice: self.show_reports()
        )
        top_n_menu.pack(side="left", padx=(0, 10))

        refresh_button = ctk.CTkButton(
            controls_frame,
            text="↻ Refresh Reports",
            width=145,
            height=38,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.show_reports
        )
        refresh_button.pack(side="left")

        try:
            top_n = int(self.report_top_n_var.get().split()[1])
        except Exception:
            top_n = 8

        summary_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        summary_frame.pack(fill="x", pady=(20, 16))

        for i in range(5):
            summary_frame.grid_columnconfigure(i, weight=1)

        self.create_report_summary_card(
            summary_frame,
            0,
            "TOTAL PRODUCTS",
            f"{stats.get('total_products', 0)} SKUs",
            f"Across {total_categories} categories",
            BLUE
        )
        self.create_report_summary_card(
            summary_frame,
            1,
            "TOTAL UNITS IN STOCK",
            f"{total_units:,} Units",
            "Available physical inventory",
            NAVY
        )
        self.create_report_summary_card(
            summary_frame,
            2,
            "TOTAL STOCK VALUE",
            f"₹{total_stock_val:,.2f}",
            "Valuation at unit price",
            GREEN
        )
        self.create_report_summary_card(
            summary_frame,
            3,
            "LOW STOCK ALERTS",
            f"{stats.get('low_stock', 0)} Items",
            "Stock between 1 and 10 units",
            ORANGE
        )
        self.create_report_summary_card(
            summary_frame,
            4,
            "OUT OF STOCK",
            f"{stats.get('out_of_stock', 0)} Items",
            "Immediate restock required",
            RED
        )

        report_container = ctk.CTkFrame(self.content, fg_color="transparent")
        report_container.pack(fill="both", expand=True)
        report_container.grid_columnconfigure(0, weight=3)
        report_container.grid_columnconfigure(1, weight=2)
        report_container.grid_rowconfigure(0, weight=1)
        report_container.grid_rowconfigure(1, weight=1)

        category_chart = self.create_chart_panel(
            report_container,
            0,
            0,
            f"Top {top_n} Categories by Stock Quantity",
            "Ranked highest to lowest by total physical units in stock"
        )
        self.create_category_quantity_chart(
            category_chart,
            category_quantity,
            top_n=top_n
        )

        distribution_chart = self.create_chart_panel(
            report_container,
            0,
            1,
            "Unit Share by Category",
            "Top 6 categories vs. all remaining categories"
        )
        self.create_stock_distribution_chart(
            distribution_chart,
            category_quantity,
            total_units=total_units
        )

        value_chart = self.create_chart_panel(
            report_container,
            1,
            0,
            f"Top {top_n} Categories by Stock Value (₹)",
            "Highest-value inventory categories (Quantity × Unit Price)"
        )
        self.create_category_value_chart(
            value_chart,
            category_value,
            top_n=top_n
        )

        status_chart = self.create_chart_panel(
            report_container,
            1,
            1,
            "Inventory Health & Stock Status",
            "Breakdown of In Stock, Low Stock, and Out of Stock SKUs"
        )
        self.create_stock_status_chart(
            status_chart,
            stock_status,
            total_products=int(stats.get("total_products", 0))
        )

        tables_container = ctk.CTkFrame(self.content, fg_color="transparent")
        tables_container.pack(fill="both", expand=True, pady=(14, 0))
        tables_container.grid_columnconfigure(0, weight=3)
        tables_container.grid_columnconfigure(1, weight=2)

        cat_table_panel = ctk.CTkFrame(
            tables_container,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        cat_table_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=6)

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

    # ========================================================
    # REPORT SUMMARY CARD (WITH SUBTITLE CONTEXT)
    # ========================================================
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

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 10))

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

    # ========================================================
    # CHART PANEL
    # ========================================================
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

    # ========================================================
    # CHART 1: HORIZONTAL RANKED BAR - QUANTITY BY CATEGORY
    # ========================================================
    def create_category_quantity_chart(self, parent, data, top_n=8):
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
            quantities = [v for _, v in reversed(top_items)]

            bar_colors = [
                NAVY if i == len(quantities) - 1 else BLUE
                for i in range(len(quantities))
            ]
            bars = ax.barh(
                categories,
                quantities,
                color=bar_colors,
                height=0.62,
                edgecolor="none"
            )

            max_val = max(quantities) if quantities else 1
            ax.set_xlim(0, max_val * 1.22 if max_val > 0 else 10)
            ax.set_xlabel("Stock Quantity (Units)", fontsize=9, color=MUTED)
            ax.tick_params(axis="y", labelsize=8.5, colors=TEXT, length=0)
            ax.tick_params(axis="x", labelsize=8, colors=MUTED)
            ax.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1")
            ax.set_axisbelow(True)

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

    # ========================================================
    # CHART 2: DONUT CHART - STOCK DISTRIBUTION (TOP 6 + OTHERS)
    # ========================================================
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
            ax.axis("off")
        else:
            sorted_items = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
            top_slices = sorted_items[:6]
            other_slices = sorted_items[6:]

            labels = []
            values = []
            for k, v in top_slices:
                short_k = k if len(k) <= 17 else k[:15] + "…"
                labels.append(short_k)
                values.append(v)

            if other_slices:
                other_sum = sum(v for _, v in other_slices)
                labels.append(f"Others ({len(other_slices)} cats)")
                values.append(other_sum)

            colors = CHART_PALETTE[:len(values)]
            total = sum(values) or 1

            wedges, _ = ax.pie(
                values,
                colors=colors,
                startangle=140,
                radius=1.0,
                wedgeprops={"width": 0.42, "edgecolor": WHITE, "linewidth": 2}
            )

            ax.text(
                0, 0.08,
                f"{total_units:,}",
                ha="center", va="center",
                fontsize=15, fontweight="bold", color=TEXT
            )
            ax.text(
                0, -0.18,
                "Total Units",
                ha="center", va="center",
                fontsize=8.5, color=MUTED
            )

            legend_labels = [
                f"{lbl}: {val:,} ({val / total * 100:.1f}%)"
                for lbl, val in zip(labels, values)
            ]
            ax.legend(
                wedges,
                legend_labels,
                loc="center left",
                bbox_to_anchor=(0.95, 0.5),
                frameon=False,
                fontsize=8,
                labelcolor=TEXT
            )
            ax.set_aspect("equal")

        figure.subplots_adjust(left=0.02, right=0.52, top=0.94, bottom=0.06)
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 12))

    # ========================================================
    # CHART 3: HORIZONTAL RANKED BAR - STOCK VALUE BY CATEGORY
    # ========================================================
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

    # ========================================================
    # CHART 4: DONUT CHART - STOCK AVAILABILITY STATUS
    # ========================================================
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

    # ========================================================
    # REPORTS HELPER TABLES (COMPLETE CATEGORY & RESTOCK LIST)
    # ========================================================
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

    # ========================================================
    # REDESIGNED SETTINGS (STORE PROFILE, BILLING & DB ADMIN)
    # ========================================================
    def show_settings(self):
        self.clear_content()

        # Header
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left")

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

        # Two-Column Settings Workspace
        workspace = ctk.CTkFrame(self.content, fg_color="transparent")
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=3)
        workspace.grid_columnconfigure(1, weight=2)

        # ----------------------------------------------------
        # LEFT COLUMN: STORE PROFILE & POS BILLING DEFAULTS
        # ----------------------------------------------------
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

        self._settings_entries = {}

        def add_setting_field(row_idx, col_idx, key, label_text, colspan=1):
            cell = ctk.CTkFrame(form_frame, fg_color="transparent")
            cell.grid(
                row=row_idx,
                column=col_idx,
                columnspan=colspan,
                sticky="we",
                padx=6,
                pady=6
            )
            ctk.CTkLabel(
                cell,
                text=label_text,
                text_color=TEXT,
                font=self.font_bold_12,
                anchor="w"
            ).pack(anchor="w", pady=(0, 4))
            ent = ctk.CTkEntry(
                cell,
                height=36,
                border_color=BORDER,
                fg_color=WHITE
            )
            ent.pack(fill="x")
            ent.insert(0, str(self.app_settings.get(key, "")))
            self._settings_entries[key] = ent

        add_setting_field(0, 0, "store_name", "Store / Brand Name")
        add_setting_field(0, 1, "invoice_prefix", "Invoice Number Prefix (e.g. INV)")
        add_setting_field(1, 0, "store_tagline", "Receipt Subtitle / Tagline", colspan=2)
        add_setting_field(2, 0, "store_address", "Store Location / Address", colspan=2)
        add_setting_field(3, 0, "store_contact", "Store Phone & GSTIN (Printed on Receipt)", colspan=2)
        add_setting_field(4, 0, "default_tax_pct", "Default POS Tax / GST (%)")
        add_setting_field(4, 1, "default_discount_pct", "Default POS Discount (%)")
        add_setting_field(5, 0, "low_stock_threshold", "Low Stock Alert Threshold (Units)")

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

        # ----------------------------------------------------
        # RIGHT COLUMN: DATABASE HEALTH, BACKUP & MAINTENANCE
        # ----------------------------------------------------
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

        db_path = self._get_billing_db_path()
        try:
            size_kb = db_path.stat().st_size / 1024.0 if db_path.exists() else 0.0
        except Exception:
            size_kb = 0.0

        stats = get_dashboard_stats()
        inv_count, total_rev = self._get_sales_summary_stats()

        diag_box = ctk.CTkFrame(
            db_card,
            fg_color=PAGE_BG,
            corner_radius=8,
            border_width=1,
            border_color=BORDER
        )
        diag_box.pack(fill="x", padx=24, pady=(4, 14))

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

        # Maintenance & Backup Buttons
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

    def _on_save_settings_click(self):
        new_vals = {}
        for k, ent in self._settings_entries.items():
            new_vals[k] = ent.get().strip()

        if not new_vals.get("store_name"):
            messagebox.showwarning("Validation", "Store Name cannot be empty.", parent=self)
            return

        try:
            tax_f = float(new_vals.get("default_tax_pct", "18"))
            disc_f = float(new_vals.get("default_discount_pct", "0"))
            thresh_i = int(float(new_vals.get("low_stock_threshold", "10")))
            if tax_f < 0 or disc_f < 0 or disc_f > 100 or thresh_i < 1:
                raise ValueError
            new_vals["default_tax_pct"] = str(tax_f)
            new_vals["default_discount_pct"] = str(disc_f)
            new_vals["low_stock_threshold"] = str(thresh_i)
        except ValueError:
            messagebox.showerror(
                "Invalid Numeric Setting",
                "Tax % (≥ 0), Discount % (0–100), and Low Stock Threshold (≥ 1) must be valid numbers.",
                parent=self
            )
            return

        self._save_app_settings(new_vals)
        messagebox.showinfo(
            "Settings Saved",
            "Store profile, billing defaults, and stock alert thresholds have been updated.",
            parent=self
        )
        self.show_settings()

    def _on_restore_default_settings(self):
        confirm = messagebox.askyesno(
            "Restore Default Settings",
            "Restore all store and billing settings to their default values?",
            parent=self
        )
        if not confirm:
            return
        self._save_app_settings(self._default_settings())
        self.show_settings()

    def _backup_database_file(self):
        db_path = self._get_billing_db_path()
        if not db_path.exists():
            messagebox.showwarning("No Database", "Database file does not exist yet.", parent=self)
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = filedialog.asksaveasfilename(
            title="Save Database Backup",
            defaultextension=".db",
            initialfile=f"inventory_backup_{stamp}.db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not dest:
            return
        try:
            shutil.copy2(str(db_path), str(dest))
            messagebox.showinfo(
                "Backup Complete",
                f"Database backup saved successfully to:\n{dest}",
                parent=self
            )
        except Exception as exc:
            messagebox.showerror("Backup Error", f"Could not back up database:\n{exc}", parent=self)

    def _optimize_database(self):
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("VACUUM;")
                conn.execute("ANALYZE;")
            messagebox.showinfo(
                "Optimization Complete",
                "SQLite VACUUM and ANALYZE completed. Database storage is compacted and indexed for fast queries.",
                parent=self
            )
            self.show_settings()
        except Exception as exc:
            messagebox.showerror("Optimization Error", str(exc), parent=self)

    def _clear_all_invoice_history(self):
        confirm = messagebox.askyesno(
            "Clear Invoice History",
            "Are you sure you want to delete all past invoices and billing history?\n\nYour inventory products will NOT be deleted.",
            parent=self
        )
        if not confirm:
            return
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("DELETE FROM invoice_items;")
                conn.execute("DELETE FROM invoices;")
                conn.commit()
            messagebox.showinfo("Cleared", "All invoice history has been cleared.", parent=self)
            self.show_settings()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    def _factory_reset_inventory(self):
        confirm = messagebox.askyesno(
            "Factory Reset Inventory",
            "WARNING: This will permanently delete ALL products from your inventory database!\n\nAre you sure you want to continue?",
            parent=self
        )
        if not confirm:
            return
        db_path = self._get_billing_db_path()
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("DELETE FROM products;")
                conn.commit()
            self.cart_items.clear()
            messagebox.showinfo("Reset Complete", "All inventory products have been removed.", parent=self)
            self.show_settings()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)

    # ========================================================
    # CREATE INVOICE SHORTCUT (OPENS BILLING WORKSPACE)
    # ========================================================
    def create_invoice(self):
        self.show_page("Billing")
        self._shortcut_focus_scan_search()


# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()