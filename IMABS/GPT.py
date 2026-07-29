import sys
from pathlib import Path

import customtkinter as ctk
from tkinter import ttk, messagebox


# ============================================================
# CONNECT TO DATABASE.PY
# ============================================================

PROJECT_ROOT = Path('School-project/Database/database.py').resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database import (
    initialize_database,
    add_product,
    get_products,
    search_products,
    update_product,
    delete_product,
    get_dashboard_stats
)


# ============================================================
# APP SETTINGS
# ============================================================

ctk.set_appearance_mode("light")

ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

NAVY = "#172554"
NAVY_HOVER = "#263A70"

BLUE = "#2563EB"
BLUE_HOVER = "#1D4ED8"

PAGE_BG = "#F4F6FA"

WHITE = "#FFFFFF"

TEXT = "#111827"
SECONDARY_TEXT = "#64748B"

BORDER = "#E2E8F0"

GREEN = "#16A34A"
RED = "#DC2626"
ORANGE = "#EA580C"


# ============================================================
# MAIN APPLICATION
# ============================================================

class DashboardApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        # Make sure database/table exists
        initialize_database()

        self.title("IMABS - Inventory Management System")

        self.geometry("1400x830")

        self.minsize(1100, 700)

        self.configure(
            fg_color=PAGE_BG
        )

        # Grid configuration
        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # Build interface
        self.create_sidebar()

        self.create_main_area()

        # Start dashboard
        self.show_dashboard()


    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=210,
            corner_radius=0,
            fg_color=NAVY
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)


        # ---------------- LOGO ----------------

        logo = ctk.CTkLabel(
            self.sidebar,
            text="IMABS",
            text_color=WHITE,
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            )
        )

        logo.pack(
            anchor="w",
            padx=30,
            pady=(35, 50)
        )


        # ---------------- NAVIGATION ----------------

        self.nav_buttons = {}

        navigation = [
            "Dashboard",
            "Inventory",
            "Billing",
            "Reports",
            "Settings"
        ]

        for item in navigation:

            button = ctk.CTkButton(
                self.sidebar,
                text=item,
                anchor="w",
                height=42,
                corner_radius=7,
                fg_color="transparent",
                hover_color=NAVY_HOVER,
                text_color="#E2E8F0",
                font=ctk.CTkFont(
                    size=14
                ),
                command=lambda page=item:
                self.navigate(page)
            )

            button.pack(
                fill="x",
                padx=18,
                pady=3
            )

            self.nav_buttons[item] = button


    # ========================================================
    # MAIN AREA
    # ========================================================

    def create_main_area(self):

        self.main_area = ctk.CTkFrame(
            self,
            fg_color=PAGE_BG,
            corner_radius=0
        )

        self.main_area.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main_area.grid_rowconfigure(
            1,
            weight=1
        )

        self.main_area.grid_columnconfigure(
            0,
            weight=1
        )


        # ---------------- TOP BAR ----------------

        self.topbar = ctk.CTkFrame(
            self.main_area,
            height=75,
            fg_color=WHITE,
            corner_radius=0
        )

        self.topbar.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.topbar.grid_columnconfigure(
            0,
            weight=1
        )


        # Search
        self.global_search = ctk.CTkEntry(
            self.topbar,
            width=380,
            height=38,
            placeholder_text="Search inventory..."
        )

        self.global_search.grid(
            row=0,
            column=0,
            padx=35,
            pady=18,
            sticky="w"
        )

        self.global_search.bind(
            "<Return>",
            self.global_search_event
        )


        # Create invoice button
        invoice_button = ctk.CTkButton(
            self.topbar,
            text="+ Create Invoice",
            width=140,
            height=38,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            command=self.create_invoice
        )

        invoice_button.grid(
            row=0,
            column=1,
            padx=35,
            pady=18
        )


        # ---------------- CONTENT FRAME ----------------

        self.content_frame = ctk.CTkFrame(
            self.main_area,
            fg_color=PAGE_BG,
            corner_radius=0
        )

        self.content_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )


    # ========================================================
    # NAVIGATION
    # ========================================================

    def navigate(self, page):

        # Change active button

        for name, button in self.nav_buttons.items():

            if name == page:

                button.configure(
                    fg_color=NAVY_HOVER,
                    text_color=WHITE,
                    font=ctk.CTkFont(
                        size=14,
                        weight="bold"
                    )
                )

            else:

                button.configure(
                    fg_color="transparent",
                    text_color="#E2E8F0",
                    font=ctk.CTkFont(
                        size=14
                    )
                )


        # Open selected page

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
    # CLEAR PAGE
    # ========================================================

    def clear_page(self):

        for widget in self.content_frame.winfo_children():

            widget.destroy()


    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.clear_page()

        self.navigate_active("Dashboard")


        # ---------------- TITLE ----------------

        title = ctk.CTkLabel(
            self.content_frame,
            text="Overview",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=35,
            pady=(30, 5)
        )


        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Inventory and business overview",
            text_color=SECONDARY_TEXT,
            font=ctk.CTkFont(
                size=14
            )
        )

        subtitle.pack(
            anchor="w",
            padx=35,
            pady=(0, 20)
        )


        # ---------------- STATISTICS ----------------

        stats = get_dashboard_stats()


        cards = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        cards.pack(
            fill="x",
            padx=35
        )

        for i in range(4):

            cards.grid_columnconfigure(
                i,
                weight=1
            )


        self.create_stat_card(
            cards,
            0,
            "TOTAL STOCK VALUE",
            f"₹{stats['total_stock_value']:,.2f}"
        )

        self.create_stat_card(
            cards,
            1,
            "LOW STOCK",
            f"{stats['low_stock']} Items"
        )

        self.create_stat_card(
            cards,
            2,
            "TOTAL PRODUCTS",
            str(stats["total_products"])
        )

        self.create_stat_card(
            cards,
            3,
            "DATABASE",
            "Connected"
        )


        # ---------------- INVENTORY PREVIEW ----------------

        panel = ctk.CTkFrame(
            self.content_frame,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )


        heading = ctk.CTkLabel(
            panel,
            text="Recent Inventory",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        heading.pack(
            anchor="w",
            padx=25,
            pady=(20, 15)
        )


        self.create_dashboard_table(panel)


    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(
        self,
        parent,
        column,
        label,
        value
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=6
        )


        ctk.CTkLabel(
            card,
            text=label,
            text_color="#2563EB",
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )


        ctk.CTkLabel(
            card,
            text=value,
            text_color=TEXT,
            font=ctk.CTkFont(
                size=23,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )


    # ========================================================
    # DASHBOARD TABLE
    # ========================================================

    def create_dashboard_table(self, parent):

        columns = (
            "sku",
            "name",
            "category",
            "quantity",
            "price",
            "status"
        )

        tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            height=10
        )

        headings = {
            "sku": "SKU",
            "name": "Product Name",
            "category": "Category",
            "quantity": "Quantity",
            "price": "Price",
            "status": "Status"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

        tree.column(
            "sku",
            width=120
        )

        tree.column(
            "name",
            width=240
        )

        tree.column(
            "category",
            width=170
        )

        tree.column(
            "quantity",
            width=100
        )

        tree.column(
            "price",
            width=120
        )

        tree.column(
            "status",
            width=130
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )


        for product in get_products()[:8]:

            tree.insert(
                "",
                "end",
                values=(
                    product[1],
                    product[2],
                    product[3],
                    product[4],
                    f"₹{product[5]:,.2f}",
                    product[6]
                )
            )


    # ========================================================
    # INVENTORY PAGE
    # ========================================================

    def show_inventory(self):

        self.clear_page()

        self.navigate_active("Inventory")


        # ---------------- HEADER ----------------

        header = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 15)
        )


        title = ctk.CTkLabel(
            header,
            text="Inventory",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        title.pack(
            side="left"
        )


        add_button = ctk.CTkButton(
            header,
            text="+ Add Product",
            width=145,
            height=40,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.open_add_product
        )

        add_button.pack(
            side="right"
        )


        # ---------------- SEARCH ----------------

        search_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )


        self.inventory_search = ctk.CTkEntry(
            search_frame,
            width=420,
            height=38,
            placeholder_text="Search SKU, product, category..."
        )

        self.inventory_search.pack(
            side="left"
        )


        self.inventory_search.bind(
            "<KeyRelease>",
            self.inventory_search_event
        )


        # ---------------- TABLE PANEL ----------------

        panel = ctk.CTkFrame(
            self.content_frame,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 25)
        )


        self.create_inventory_table(panel)


    # ========================================================
    # INVENTORY TABLE
    # ========================================================

    def create_inventory_table(self, parent):

        columns = (
            "id",
            "sku",
            "name",
            "category",
            "quantity",
            "price",
            "status"
        )


        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Inventory.Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=TEXT,
            rowheight=38,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "Inventory.Treeview.Heading",
            background="#F8FAFC",
            foreground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.map(
            "Inventory.Treeview",
            background=[
                ("selected", "#DBEAFE")
            ],
            foreground=[
                ("selected", TEXT)
            ]
        )


        self.inventory_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Inventory.Treeview"
        )


        headings = {
            "id": "ID",
            "sku": "SKU",
            "name": "Product Name",
            "category": "Category",
            "quantity": "Quantity",
            "price": "Price",
            "status": "Status"
        }


        for column in columns:

            self.inventory_tree.heading(
                column,
                text=headings[column]
            )


        self.inventory_tree.column(
            "id",
            width=50
        )

        self.inventory_tree.column(
            "sku",
            width=110
        )

        self.inventory_tree.column(
            "name",
            width=250
        )

        self.inventory_tree.column(
            "category",
            width=160
        )

        self.inventory_tree.column(
            "quantity",
            width=100
        )

        self.inventory_tree.column(
            "price",
            width=120
        )

        self.inventory_tree.column(
            "status",
            width=130
        )


        self.inventory_tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        # Double click to edit
        self.inventory_tree.bind(
            "<Double-1>",
            self.edit_selected_product
        )


        # Load database
        self.refresh_inventory()


    # ========================================================
    # REFRESH INVENTORY
    # ========================================================

    def refresh_inventory(self, products=None):

        if not hasattr(
            self,
            "inventory_tree"
        ):

            return


        # Clear table

        for item in self.inventory_tree.get_children():

            self.inventory_tree.delete(item)


        # Get products

        if products is None:

            products = get_products()


        # Insert products

        for product in products:

            self.inventory_tree.insert(
                "",
                "end",
                values=(
                    product[0],
                    product[1],
                    product[2],
                    product[3],
                    product[4],
                    f"₹{product[5]:,.2f}",
                    product[6]
                )
            )


    # ========================================================
    # SEARCH INVENTORY
    # ========================================================

    def inventory_search_event(self, event=None):

        search = self.inventory_search.get().strip()


        if search == "":

            self.refresh_inventory()

        else:

            products = search_products(
                search
            )

            self.refresh_inventory(
                products
            )


    # ========================================================
    # ADD PRODUCT WINDOW
    # ========================================================

    def open_add_product(self):

        window = ctk.CTkToplevel(self)

        window.title("Add Product")

        window.geometry("480x570")

        window.resizable(
            False,
            False
        )

        window.grab_set()


        # ---------------- TITLE ----------------

        ctk.CTkLabel(
            window,
            text="Add New Product",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(
            pady=(25, 25)
        )


        # ---------------- FORM ----------------

        entries = {}


        fields = [
            ("SKU", "Example: SKU-001"),
            ("Product Name", "Example: Wireless Mouse"),
            ("Category", "Example: Electronics"),
            ("Quantity", "Example: 25"),
            ("Price", "Example: 799")
        ]


        for label, placeholder in fields:

            ctk.CTkLabel(
                window,
                text=label,
                text_color=TEXT,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=45
            )


            entry = ctk.CTkEntry(
                window,
                height=38,
                placeholder_text=placeholder
            )

            entry.pack(
                fill="x",
                padx=45,
                pady=(5, 14)
            )


            entries[label] = entry


        # ---------------- SAVE FUNCTION ----------------

        def save():

            sku = entries["SKU"].get().strip()

            name = entries["Product Name"].get().strip()

            category = entries["Category"].get().strip()

            quantity_text = entries["Quantity"].get().strip()

            price_text = entries["Price"].get().strip()


            # Empty check

            if not all([
                sku,
                name,
                category,
                quantity_text,
                price_text
            ]):

                messagebox.showwarning(
                    "Missing Information",
                    "Please fill all fields.",
                    parent=window
                )

                return


            # Number validation

            try:

                quantity = int(
                    quantity_text
                )

                price = float(
                    price_text
                )


                if quantity < 0:

                    raise ValueError


                if price < 0:

                    raise ValueError


            except ValueError:

                messagebox.showerror(
                    "Invalid Data",
                    "Quantity must be a positive whole number\n"
                    "and price must be a valid number.",
                    parent=window
                )

                return


            # Save to database

            success, message = add_product(
                sku,
                name,
                category,
                quantity,
                price
            )


            if not success:

                messagebox.showerror(
                    "Cannot Add Product",
                    message,
                    parent=window
                )

                return


            messagebox.showinfo(
                "Success",
                "Product added successfully!",
                parent=window
            )


            # Close window

            window.destroy()


            # Refresh current inventory page

            self.refresh_inventory()


        # ---------------- SAVE BUTTON ----------------

        ctk.CTkButton(
            window,
            text="Save Product",
            height=42,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=save
        ).pack(
            fill="x",
            padx=45,
            pady=(5, 20)
        )


    # ========================================================
    # EDIT PRODUCT
    # ========================================================

    def edit_selected_product(self, event=None):

        selected = self.inventory_tree.selection()


        if not selected:

            return


        values = self.inventory_tree.item(
            selected[0],
            "values"
        )


        product_id = int(
            values[0]
        )


        self.open_edit_product(
            product_id,
            values
        )


    # ========================================================
    # EDIT PRODUCT WINDOW
    # ========================================================

    def open_edit_product(
        self,
        product_id,
        values
    ):

        window = ctk.CTkToplevel(self)

        window.title("Edit Product")

        window.geometry("480x570")

        window.resizable(
            False,
            False
        )

        window.grab_set()


        ctk.CTkLabel(
            window,
            text="Edit Product",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(
            pady=(25, 25)
        )


        fields = [
            ("SKU", values[1]),
            ("Product Name", values[2]),
            ("Category", values[3]),
            ("Quantity", values[4]),
            ("Price", values[5].replace("₹", ""))
        ]


        entries = {}


        for label, value in fields:

            ctk.CTkLabel(
                window,
                text=label,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=45
            )


            entry = ctk.CTkEntry(
                window,
                height=38
            )

            entry.insert(
                0,
                value
            )

            entry.pack(
                fill="x",
                padx=45,
                pady=(5, 14)
            )


            entries[label] = entry


        # ---------------- UPDATE ----------------

        def update():

            sku = entries["SKU"].get().strip()

            name = entries["Product Name"].get().strip()

            category = entries["Category"].get().strip()

            quantity_text = entries["Quantity"].get().strip()

            price_text = entries["Price"].get().strip()


            if not all([
                sku,
                name,
                category,
                quantity_text,
                price_text
            ]):

                messagebox.showwarning(
                    "Missing Information",
                    "Please fill all fields.",
                    parent=window
                )

                return


            try:

                quantity = int(
                    quantity_text
                )

                price = float(
                    price_text
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid Data",
                    "Please enter valid quantity and price.",
                    parent=window
                )

                return


            success, message = update_product(
                product_id,
                sku,
                name,
                category,
                quantity,
                price
            )


            if not success:

                messagebox.showerror(
                    "Update Failed",
                    message,
                    parent=window
                )

                return


            window.destroy()

            self.refresh_inventory()

            messagebox.showinfo(
                "Updated",
                "Product updated successfully!"
            )


        ctk.CTkButton(
            window,
            text="Update Product",
            height=42,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=update
        ).pack(
            fill="x",
            padx=45,
            pady=(5, 10)
        )


        # ---------------- DELETE ----------------

        def remove():

            confirm = messagebox.askyesno(
                "Delete Product",
                "Are you sure you want to delete this product?",
                parent=window
            )


            if not confirm:

                return


            delete_product(
                product_id
            )


            window.destroy()

            self.refresh_inventory()


            messagebox.showinfo(
                "Deleted",
                "Product deleted successfully!"
            )


        ctk.CTkButton(
            window,
            text="Delete Product",
            height=38,
            fg_color=RED,
            hover_color="#B91C1C",
            command=remove
        ).pack(
            fill="x",
            padx=45
        )


    # ========================================================
    # BILLING
    # ========================================================

    def show_billing(self):

        self.clear_page()

        self.navigate_active("Billing")


        ctk.CTkLabel(
            self.content_frame,
            text="Billing",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 10)
        )


        ctk.CTkLabel(
            self.content_frame,
            text="Billing system will be added next.",
            text_color=SECONDARY_TEXT,
            font=ctk.CTkFont(
                size=15
            )
        ).pack(
            anchor="w",
            padx=35
        )


    # ========================================================
    # REPORTS
    # ========================================================

    def show_reports(self):

        self.clear_page()

        self.navigate_active("Reports")


        ctk.CTkLabel(
            self.content_frame,
            text="Reports",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 10)
        )


        ctk.CTkLabel(
            self.content_frame,
            text="Reports and analytics will be added next.",
            text_color=SECONDARY_TEXT
        ).pack(
            anchor="w",
            padx=35
        )


    # ========================================================
    # SETTINGS
    # ========================================================

    def show_settings(self):

        self.clear_page()

        self.navigate_active("Settings")


        ctk.CTkLabel(
            self.content_frame,
            text="Settings",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 10)
        )


        ctk.CTkLabel(
            self.content_frame,
            text="Application settings will be added next.",
            text_color=SECONDARY_TEXT
        ).pack(
            anchor="w",
            padx=35
        )


    # ========================================================
    # ACTIVE NAVIGATION
    # ========================================================

    def navigate_active(self, page):

        for name, button in self.nav_buttons.items():

            if name == page:

                button.configure(
                    fg_color=NAVY_HOVER,
                    text_color=WHITE
                )

            else:

                button.configure(
                    fg_color="transparent",
                    text_color="#E2E8F0"
                )


    # ========================================================
    # GLOBAL SEARCH
    # ========================================================

    def global_search_event(self, event=None):

        search = self.global_search.get().strip()


        if search:

            self.show_inventory()

            self.inventory_search.insert(
                0,
                search
            )

            self.inventory_search_event()


    # ========================================================
    # CREATE INVOICE
    # ========================================================

    def create_invoice(self):

        messagebox.showinfo(
            "Billing",
            "Invoice system will be connected to the database in the next stage."
        )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = DashboardApp()

    app.mainloop()