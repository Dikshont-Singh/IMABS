import sys
from pathlib import Path
<<<<<<< HEAD
from collections import defaultdict
=======

>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75

# ============================================================
# FIX IMPORT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
<<<<<<< HEAD
    sys.path.insert(0, str(PROJECT_ROOT))
=======

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75


# ============================================================
# IMPORTS
# ============================================================

import customtkinter as ctk

from tkinter import (
    ttk,
    filedialog,
    messagebox
)

<<<<<<< HEAD
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

=======
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75

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


# ============================================================
# APPEARANCE
# ============================================================

ctk.set_appearance_mode("light")

ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

NAVY = "#172554"
<<<<<<< HEAD
NAVY_HOVER = "#243B78"

BLUE = "#2563EB"
BLUE_HOVER = "#1D4ED8"

GREEN = "#0F766E"
GREEN_HOVER = "#115E59"

RED = "#DC2626"
RED_HOVER = "#B91C1C"

ORANGE = "#D97706"

GRAY = "#64748B"
GRAY_HOVER = "#475569"

PAGE_BG = "#F4F6FA"
WHITE = "#FFFFFF"

BORDER = "#E2E8F0"

TEXT = "#0F172A"
MUTED = "#64748B"


# ============================================================
# SIDEBAR BUTTON
# ============================================================

class SidebarButton(ctk.CTkButton):

    def __init__(
        self,
        master,
        text,
        command=None
    ):

        super().__init__(
            master,
            text=text,
            command=command,
            anchor="w",
            height=42,
            corner_radius=7,
            fg_color="transparent",
            hover_color=NAVY_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=14
            )
        )


    def set_active(self, active):

        if active:

            self.configure(
                fg_color=NAVY_HOVER,
                font=ctk.CTkFont(
                    size=14,
                    weight="bold"
                )
            )

        else:

            self.configure(
                fg_color="transparent",
                font=ctk.CTkFont(
                    size=14
                )
            )


# ============================================================
# DASHBOARD APPLICATION
# ============================================================

class DashboardApp(ctk.CTk):

    def __init__(self):

        super().__init__()


=======

NAVY_HOVER = "#243B78"

BLUE = "#2563EB"

BLUE_HOVER = "#1D4ED8"

GREEN = "#0F766E"

GREEN_HOVER = "#115E59"

RED = "#DC2626"

RED_HOVER = "#B91C1C"

GRAY = "#64748B"

GRAY_HOVER = "#475569"

PAGE_BG = "#F4F6FA"

WHITE = "#FFFFFF"

BORDER = "#E2E8F0"

TEXT = "#0F172A"

MUTED = "#64748B"


# ============================================================
# SIDEBAR BUTTON
# ============================================================

class SidebarButton(ctk.CTkButton):

    def __init__(
        self,
        master,
        text,
        command=None
    ):

        super().__init__(
            master,
            text=text,
            command=command,
            anchor="w",
            height=42,
            corner_radius=7,
            fg_color="transparent",
            hover_color=NAVY_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=14
            )
        )


    def set_active(self, active):

        if active:

            self.configure(
                fg_color=NAVY_HOVER,
                font=ctk.CTkFont(
                    size=14,
                    weight="bold"
                )
            )

        else:

            self.configure(
                fg_color="transparent",
                font=ctk.CTkFont(
                    size=14
                )
            )


# ============================================================
# DASHBOARD APPLICATION
# ============================================================

class DashboardApp(ctk.CTk):

    def __init__(self):

        super().__init__()


>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        initialize_database()


        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.title(
            "IMABS - Inventory Management System"
        )

        self.geometry(
            "1400x830"
        )

        self.minsize(
            1100,
            650
        )

        self.configure(
            fg_color=PAGE_BG
        )


        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )


        # ----------------------------------------------------
        # BUILD GUI
        # ----------------------------------------------------

        self.build_sidebar()

        self.build_main_area()


        # ----------------------------------------------------
        # START DASHBOARD
        # ----------------------------------------------------

        self.show_page(
            "Dashboard"
        )


    # ========================================================
    # SIDEBAR
    # ========================================================

    def build_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=165,
            corner_radius=0,
            fg_color=NAVY
        )

        sidebar.grid(
            row=0,
            column=0,
            sticky="nswe"
        )

        sidebar.grid_propagate(
            False
        )


        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo = ctk.CTkLabel(
            sidebar,
            text="IMABS",
            text_color=WHITE,
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            )
        )

        logo.pack(
            pady=(35, 45)
        )


        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

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
                command=lambda name=item:
                    self.show_page(name)
            )

            button.pack(
                fill="x",
                padx=8,
                pady=4
            )

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

        self.main.grid(
            row=0,
            column=1,
            sticky="nswe"
        )

        self.main.grid_columnconfigure(
            0,
            weight=1
        )

        self.main.grid_rowconfigure(
            1,
            weight=1
        )


        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        topbar = ctk.CTkFrame(
            self.main,
            height=70,
            fg_color=WHITE,
            corner_radius=0
        )

        topbar.grid(
            row=0,
            column=0,
            sticky="we"
        )

        topbar.grid_columnconfigure(
            0,
            weight=1
        )


        self.search_var = ctk.StringVar()


        self.search_entry = ctk.CTkEntry(
            topbar,
            width=380,
            height=38,
            placeholder_text="Search inventory...",
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


        self.search_entry.bind(
            "<KeyRelease>",
            self.search_inventory
        )


        # ----------------------------------------------------
        # CREATE INVOICE
        # ----------------------------------------------------

        invoice_button = ctk.CTkButton(
            topbar,
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
            padx=30
        )


        # ----------------------------------------------------
        # CONTENT AREA
        # ----------------------------------------------------

<<<<<<< HEAD
        self.content = ctk.CTkScrollableFrame(
=======
        self.content = ctk.CTkFrame(
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
            self.main,
            fg_color=PAGE_BG,
            corner_radius=0
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nswe",
            padx=35,
            pady=30
        )

<<<<<<< HEAD

=======
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        self.content.grid_columnconfigure(
            0,
            weight=1
        )

<<<<<<< HEAD
=======
        self.content.grid_rowconfigure(
            2,
            weight=1
        )

>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75

    # ========================================================
    # CLEAR CONTENT
    # ========================================================

    def clear_content(self):

        for widget in self.content.winfo_children():

            widget.destroy()


    # ========================================================
    # PAGE NAVIGATION
    # ========================================================

    def show_page(self, page):

        for name, button in self.nav_buttons.items():

            button.set_active(
                name == page
            )


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
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        title = ctk.CTkLabel(
            self.content,
            text="Overview",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

<<<<<<< HEAD
        title.pack(
            anchor="w"
=======
        title.grid(
            row=0,
            column=0,
            sticky="w"
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


        subtitle = ctk.CTkLabel(
            self.content,
            text="Inventory and business overview",
            text_color=MUTED
        )

<<<<<<< HEAD
        subtitle.pack(
            anchor="w",
            pady=(3, 0)
=======
        subtitle.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(45, 0)
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        stats = get_dashboard_stats()


        cards = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

<<<<<<< HEAD
        cards.pack(
            fill="x",
=======
        cards.grid(
            row=1,
            column=0,
            sticky="we",
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
            pady=(30, 25)
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
            f"₹{stats['total_value']:,.2f}"
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


        # ----------------------------------------------------
        # RECENT INVENTORY
        # ----------------------------------------------------

        panel = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

<<<<<<< HEAD
        panel.pack(
            fill="both",
            expand=True
=======
        panel.grid(
            row=2,
            column=0,
            sticky="nswe"
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
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
            pady=(22, 15)
        )


        self.create_inventory_table(
            panel,
            get_products()
        )


    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(
        self,
        parent,
        column,
        title,
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
            sticky="we",
            padx=6
        )


        label = ctk.CTkLabel(
            card,
            text=title,
            text_color=BLUE,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        )

        label.pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )


        value_label = ctk.CTkLabel(
            card,
            text=value,
            text_color=TEXT,
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        value_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )


    # ========================================================
    # INVENTORY PAGE
    # ========================================================

    def show_inventory(self):

        title = ctk.CTkLabel(
            self.content,
            text="Inventory",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        title.pack(
            anchor="w"
        )


<<<<<<< HEAD
        subtitle = ctk.CTkLabel(
            self.content,
            text="Manage your products and stock",
            text_color=MUTED
        )

        subtitle.pack(
            anchor="w",
            pady=(3, 0)
        )


=======
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        # ----------------------------------------------------
        # BUTTON BAR
        # ----------------------------------------------------

        button_bar = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        button_bar.pack(
            fill="x",
            pady=(20, 20)
        )


        add_button = ctk.CTkButton(
            button_bar,
            text="+ Add Product",
            width=140,
            height=40,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.open_add_product
        )

        add_button.pack(
            side="right"
        )


        export_button = ctk.CTkButton(
            button_bar,
            text="📤 Export CSV",
            width=130,
            height=40,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            command=self.export_csv
        )

        export_button.pack(
            side="right",
            padx=(0, 10)
        )


        import_button = ctk.CTkButton(
            button_bar,
            text="📥 Import CSV",
            width=130,
            height=40,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            command=self.import_csv
        )

        import_button.pack(
            side="right",
            padx=(0, 10)
        )


        # ----------------------------------------------------
        # TABLE PANEL
        # ----------------------------------------------------

        self.inventory_panel = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

        self.inventory_panel.pack(
            fill="both",
            expand=True
        )


        self.refresh_inventory()


    # ========================================================
    # INVENTORY TABLE
    # ========================================================

    def create_inventory_table(
        self,
        parent,
        products
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )


        frame.grid_columnconfigure(
            0,
            weight=1
        )

        frame.grid_rowconfigure(
            0,
            weight=1
        )


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

        style.theme_use(
            "clam"
        )


        style.configure(
            "Inventory.Treeview",
            background="white",
            fieldbackground="white",
            foreground="#0F172A",
            rowheight=32,
            font=("Segoe UI", 10)
        )


        style.configure(
            "Inventory.Treeview.Heading",
            background="#E2E8F0",
            foreground="#0F172A",
            font=("Segoe UI", 10, "bold")
        )


        style.map(
            "Inventory.Treeview",
            background=[
                ("selected", "#DBEAFE")
            ],
            foreground=[
                ("selected", "#0F172A")
            ]
        )


        tree = ttk.Treeview(
            frame,
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


        widths = {
            "id": 50,
            "sku": 100,
            "name": 180,
            "category": 150,
            "quantity": 90,
            "price": 110,
            "status": 120
        }


        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

            tree.column(
                column,
                width=widths[column],
                anchor="w"
            )


        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )


        tree.configure(
            yscrollcommand=scrollbar.set
        )


        tree.grid(
            row=0,
            column=0,
            sticky="nswe"
        )


        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )


        # ----------------------------------------------------
        # INSERT PRODUCTS
        # ----------------------------------------------------

        for product in products:

            tree.insert(
                "",
                "end",
                values=product
            )


        return tree


    # ========================================================
    # REFRESH INVENTORY
    # ========================================================

    def refresh_inventory(self):

        if not hasattr(
            self,
            "inventory_panel"
        ):

            return


        for widget in self.inventory_panel.winfo_children():

            widget.destroy()


        products = get_products()


        self.inventory_tree = self.create_inventory_table(
            self.inventory_panel,
            products
        )


<<<<<<< HEAD
=======
        # Double click to edit
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        self.inventory_tree.bind(
            "<Double-1>",
            self.edit_selected_product
        )


<<<<<<< HEAD
=======
        # Right click menu
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        self.inventory_tree.bind(
            "<Button-3>",
            self.show_context_menu
        )


    # ========================================================
    # SEARCH
    # ========================================================

    def search_inventory(
        self,
        event=None
    ):

        if not hasattr(
            self,
            "inventory_tree"
        ):

            return


        query = self.search_var.get().strip()


        if not query:

            products = get_products()

        else:

            products = search_products(
                query
            )


<<<<<<< HEAD
=======
        # Clear table

>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        for item in self.inventory_tree.get_children():

            self.inventory_tree.delete(
                item
            )


<<<<<<< HEAD
=======
        # Add search results

>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        for product in products:

            self.inventory_tree.insert(
                "",
                "end",
                values=product
            )


    # ========================================================
    # ADD PRODUCT WINDOW
    # ========================================================

    def open_add_product(self):

        window = ctk.CTkToplevel(
            self
        )

        window.title(
            "Add Product"
        )

        window.geometry(
            "450x550"
        )

        window.resizable(
            False,
            False
        )

        window.grab_set()


        title = ctk.CTkLabel(
            window,
            text="Add New Product",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.pack(
            pady=(25, 25)
        )


        fields = {}


        field_names = [
            "SKU",
            "Product Name",
            "Category",
            "Quantity",
            "Price"
        ]


        for field in field_names:

            label = ctk.CTkLabel(
                window,
                text=field,
                anchor="w"
            )

            label.pack(
                fill="x",
                padx=40,
                pady=(8, 3)
            )


            entry = ctk.CTkEntry(
                window,
                height=38
            )

            entry.pack(
                fill="x",
                padx=40
            )


            fields[field] = entry


        def save_product():

            sku = fields["SKU"].get().strip()

            name = fields["Product Name"].get().strip()

            category = fields["Category"].get().strip()

            quantity_text = fields["Quantity"].get().strip()

            price_text = fields["Price"].get().strip()


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
                    "Quantity must be a whole number "
                    "and Price must be a number.",
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

                messagebox.showinfo(
                    "Success",
                    message,
                    parent=window
                )

                window.destroy()

                self.refresh_inventory()

                self.refresh_dashboard_if_needed()

            else:

                messagebox.showerror(
                    "Error",
                    message,
                    parent=window
                )


        save_button = ctk.CTkButton(
            window,
            text="Add Product",
            height=42,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=save_product
        )

        save_button.pack(
            fill="x",
            padx=40,
            pady=30
        )


    # ========================================================
    # EDIT PRODUCT
    # ========================================================

    def edit_selected_product(
        self,
        event=None
    ):

        selected = self.inventory_tree.selection()


        if not selected:

            return


        values = self.inventory_tree.item(
            selected[0],
            "values"
        )


        self.open_edit_product(
            values
        )


    # ========================================================
    # EDIT WINDOW
    # ========================================================

    def open_edit_product(
        self,
        values
    ):

        window = ctk.CTkToplevel(
            self
        )

        window.title(
            "Edit Product"
        )

        window.geometry(
            "450x550"
        )

        window.resizable(
            False,
            False
        )

        window.grab_set()


        title = ctk.CTkLabel(
            window,
            text="Edit Product",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.pack(
            pady=(25, 25)
        )


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
            values[5]
        ]


        for field, current in zip(
            field_names,
            current_values
        ):

            label = ctk.CTkLabel(
                window,
                text=field,
                anchor="w"
            )

            label.pack(
                fill="x",
                padx=40,
                pady=(8, 3)
            )


            entry = ctk.CTkEntry(
                window,
                height=38
            )

            entry.insert(
                0,
                str(current)
            )

            entry.pack(
                fill="x",
                padx=40
            )


            fields[field] = entry


        def save_changes():

            sku = fields["SKU"].get().strip()

            name = fields["Product Name"].get().strip()

            category = fields["Category"].get().strip()


            try:

                quantity = int(
                    fields["Quantity"].get()
                )

                price = float(
                    fields["Price"].get()
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid Data",
                    "Quantity must be an integer "
                    "and Price must be a number.",
                    parent=window
                )

                return


<<<<<<< HEAD
            if quantity < 0 or price < 0:

                messagebox.showerror(
                    "Invalid Data",
                    "Quantity and Price cannot be negative.",
                    parent=window
                )

                return


=======
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
            success, message = update_product(
                int(values[0]),
                sku,
                name,
                category,
                quantity,
                price
            )


            if success:

                messagebox.showinfo(
                    "Success",
                    message,
                    parent=window
                )

                window.destroy()

                self.refresh_inventory()

                self.refresh_dashboard_if_needed()

            else:

                messagebox.showerror(
                    "Error",
                    message,
                    parent=window
                )


        save_button = ctk.CTkButton(
            window,
            text="Save Changes",
            height=42,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=save_changes
        )

        save_button.pack(
            fill="x",
            padx=40,
            pady=30
        )


    # ========================================================
    # RIGHT CLICK MENU
    # ========================================================

    def show_context_menu(
        self,
        event
    ):

        item = self.inventory_tree.identify_row(
            event.y
        )


        if not item:

            return


        self.inventory_tree.selection_set(
            item
        )


        menu = ctk.CTkToplevel(
            self
        )

        menu.title(
            "Product Options"
        )

        menu.geometry(
            "220x130"
        )

        menu.resizable(
            False,
            False
        )

<<<<<<< HEAD
        menu.grab_set()

=======
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75

        ctk.CTkButton(
            menu,
            text="Edit Product",
            command=lambda: (
                menu.destroy(),
                self.edit_selected_product()
            )
        ).pack(
            fill="x",
            padx=20,
            pady=(20, 5)
        )


        ctk.CTkButton(
            menu,
            text="Delete Product",
            fg_color=RED,
            hover_color=RED_HOVER,
            command=lambda: (
                menu.destroy(),
                self.delete_selected_product()
            )
        ).pack(
            fill="x",
            padx=20,
            pady=5
        )


    # ========================================================
    # DELETE PRODUCT
    # ========================================================

    def delete_selected_product(self):

        selected = self.inventory_tree.selection()


        if not selected:

            return


        values = self.inventory_tree.item(
            selected[0],
            "values"
        )


        product_id = values[0]

        product_name = values[2]


        confirm = messagebox.askyesno(
            "Delete Product",
            f"Are you sure you want to delete:\n\n"
            f"{product_name}?",
            parent=self
        )


        if not confirm:

            return


        success, message = delete_product(
            int(product_id)
        )


        if success:

            messagebox.showinfo(
                "Deleted",
                message
            )

            self.refresh_inventory()

            self.refresh_dashboard_if_needed()

        else:

            messagebox.showerror(
                "Error",
                message
            )


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

            added, skipped, errors = (
                import_products_from_csv(
                    file_path
                )
            )


            self.refresh_inventory()

            self.refresh_dashboard_if_needed()


            if skipped == 0:

                messagebox.showinfo(
                    "Import Complete",
                    f"{added} products imported successfully."
                )

            else:

                error_text = "\n".join(
                    errors[:10]
                )


                if len(errors) > 10:

                    error_text += (
                        "\n\n...and more errors."
                    )


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
            filetypes=[
                ("CSV Files", "*.csv")
            ],
            initialfile="inventory_export.csv"
        )


        if not file_path:

            return


        try:

            count = export_products_to_csv(
                file_path
            )


            messagebox.showinfo(
                "Export Complete",
                f"{count} products exported successfully.\n\n"
                f"Saved to:\n{file_path}"
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

<<<<<<< HEAD
=======
        # If dashboard is currently visible,
        # rebuild it so statistics update.

>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        try:

            current_buttons = [
                name
                for name, button
                in self.nav_buttons.items()
                if button.cget("fg_color") == NAVY_HOVER
            ]


            if "Dashboard" in current_buttons:

<<<<<<< HEAD
                self.clear_content()

=======
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
                self.show_dashboard()

        except Exception:

            pass


    # ========================================================
    # BILLING
    # ========================================================

    def show_billing(self):

        title = ctk.CTkLabel(
            self.content,
            text="Billing",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        )

        title.pack(
            anchor="w"
        )


        message = ctk.CTkLabel(
            self.content,
            text="Billing module will be added here.",
            text_color=MUTED,
            font=ctk.CTkFont(
                size=16
            )
        )

        message.pack(
            pady=50
        )


    # ========================================================
    # REPORTS
    # ========================================================

    def show_reports(self):

<<<<<<< HEAD
        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        header.pack(
            fill="x"
        )


        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_frame.pack(
            side="left"
        )


        title = ctk.CTkLabel(
            title_frame,
=======
        title = ctk.CTkLabel(
            self.content,
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
            text="Reports",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        )

        title.pack(
            anchor="w"
        )


<<<<<<< HEAD
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Visual analysis of your inventory",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=MUTED
        )

        subtitle.pack(
            anchor="w",
            pady=(2, 0)
        )


        refresh_button = ctk.CTkButton(
            header,
            text="↻ Refresh Reports",
            width=150,
            height=38,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.show_reports
        )

        refresh_button.pack(
            side="right",
            pady=5
        )


        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        products = get_products()

        stats = get_dashboard_stats()


        # ----------------------------------------------------
        # SUMMARY CARDS
        # ----------------------------------------------------

        summary_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        summary_frame.pack(
            fill="x",
            pady=(25, 20)
        )


        for i in range(4):

            summary_frame.grid_columnconfigure(
                i,
                weight=1
            )


        self.create_report_summary_card(
            summary_frame,
            0,
            "TOTAL PRODUCTS",
            str(stats["total_products"]),
            BLUE
        )


        self.create_report_summary_card(
            summary_frame,
            1,
            "TOTAL STOCK VALUE",
            f"₹{stats['total_value']:,.2f}",
            GREEN
        )


        self.create_report_summary_card(
            summary_frame,
            2,
            "LOW STOCK",
            str(stats["low_stock"]),
            ORANGE
        )


        self.create_report_summary_card(
            summary_frame,
            3,
            "OUT OF STOCK",
            str(stats["out_of_stock"]),
            RED
        )


        # ----------------------------------------------------
        # REPORT CONTAINER
        # ----------------------------------------------------

        report_container = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        report_container.pack(
            fill="both",
            expand=True
        )


        report_container.grid_columnconfigure(
            0,
            weight=1
        )

        report_container.grid_columnconfigure(
            1,
            weight=1
        )

        report_container.grid_rowconfigure(
            0,
            weight=1
        )

        report_container.grid_rowconfigure(
            1,
            weight=1
        )


        # ----------------------------------------------------
        # PREPARE DATA
        # ----------------------------------------------------

        category_quantity = defaultdict(int)

        category_value = defaultdict(float)

        stock_status = defaultdict(int)


        for product in products:

            category = product[3]

            quantity = product[4]

            price = product[5]

            status = product[6]


            category_quantity[category] += quantity

            category_value[category] += (
                quantity * price
            )

            stock_status[status] += 1


        # ----------------------------------------------------
        # CHART 1
        # ----------------------------------------------------

        category_chart = self.create_chart_panel(
            report_container,
            0,
            0,
            "Inventory by Category",
            "Total quantity of products in each category"
        )


        self.create_category_quantity_chart(
            category_chart,
            category_quantity
        )


        # ----------------------------------------------------
        # CHART 2
        # ----------------------------------------------------

        distribution_chart = self.create_chart_panel(
            report_container,
            0,
            1,
            "Stock Distribution",
            "Quantity distribution across categories"
        )


        self.create_stock_distribution_chart(
            distribution_chart,
            category_quantity
        )


        # ----------------------------------------------------
        # CHART 3
        # ----------------------------------------------------

        value_chart = self.create_chart_panel(
            report_container,
            1,
            0,
            "Stock Value by Category",
            "Total monetary value of inventory"
        )


        self.create_category_value_chart(
            value_chart,
            category_value
        )


        # ----------------------------------------------------
        # CHART 4
        # ----------------------------------------------------

        status_chart = self.create_chart_panel(
            report_container,
            1,
            1,
            "Stock Status",
            "Current availability of products"
        )


        self.create_stock_status_chart(
            status_chart,
            stock_status
        )


    # ========================================================
    # REPORT SUMMARY CARD
    # ========================================================

    def create_report_summary_card(
        self,
        parent,
        column,
        title,
        value,
        accent
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
            sticky="we",
            padx=6
        )


        accent_bar = ctk.CTkFrame(
            card,
            width=5,
            height=62,
            corner_radius=3,
            fg_color=accent
        )

        accent_bar.pack(
            side="left",
            padx=(12, 5),
            pady=12
        )


        info = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        info.pack(
            side="left",
            fill="both",
            expand=True,
            pady=12
=======
        stats = get_dashboard_stats()


        report = (
            f"Total Products: {stats['total_products']}\n\n"
            f"Total Stock Value: "
            f"₹{stats['total_value']:,.2f}\n\n"
            f"Low Stock Products: "
            f"{stats['low_stock']}\n\n"
            f"Out of Stock Products: "
            f"{stats['out_of_stock']}"
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


        ctk.CTkLabel(
<<<<<<< HEAD
            info,
            text=title,
            text_color=MUTED,
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )


        ctk.CTkLabel(
            info,
            text=value,
            text_color=TEXT,
            font=ctk.CTkFont(
                size=21,
                weight="bold"
            )
        ).pack(
            anchor="w",
            pady=(4, 0)
        )


    # ========================================================
    # CHART PANEL
    # ========================================================

    def create_chart_panel(
        self,
        parent,
        row,
        column,
        title,
        subtitle
    ):

        panel = ctk.CTkFrame(
            parent,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

        panel.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6
        )


        heading = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        heading.pack(
            fill="x",
            padx=20,
            pady=(15, 0)
        )


        ctk.CTkLabel(
            heading,
            text=title,
            text_color=TEXT,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )


        ctk.CTkLabel(
            heading,
            text=subtitle,
            text_color=MUTED,
            font=ctk.CTkFont(
                size=11
            )
        ).pack(
            anchor="w",
            pady=(2, 0)
        )


        return panel


    # ========================================================
    # CHART 1
    # INVENTORY BY CATEGORY
    # ========================================================

    def create_category_quantity_chart(
        self,
        parent,
        data
    ):

        figure = Figure(
            figsize=(5, 3),
            dpi=90
        )

        figure.patch.set_facecolor(WHITE)

        ax = figure.add_subplot(111)

        ax.set_facecolor(WHITE)


        if not data:

            ax.text(
                0.5,
                0.5,
                "No inventory data",
                ha="center",
                va="center",
                fontsize=12
            )

            ax.axis("off")

        else:

            categories = list(
                data.keys()
            )

            quantities = list(
                data.values()
            )


            bars = ax.bar(
                categories,
                quantities
            )


            ax.set_ylabel(
                "Quantity",
                fontsize=9
            )


            ax.tick_params(
                axis="x",
                rotation=25,
                labelsize=8
            )

            ax.tick_params(
                axis="y",
                labelsize=8
            )


            ax.grid(
                axis="y",
                alpha=0.2
            )


            ax.set_axisbelow(True)


            # Remove unnecessary borders

            ax.spines["top"].set_visible(False)

            ax.spines["right"].set_visible(False)


            # Values above bars

            for bar, value in zip(
                bars,
                quantities
            ):

                ax.text(
                    bar.get_x()
                    + bar.get_width() / 2,
                    bar.get_height(),
                    str(value),
                    ha="center",
                    va="bottom",
                    fontsize=8
                )


        figure.tight_layout()


        canvas = FigureCanvasTkAgg(
            figure,
            master=parent
        )

        canvas.draw()


        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )


    # ========================================================
    # CHART 2
    # STOCK DISTRIBUTION
    # ========================================================

    def create_stock_distribution_chart(
        self,
        parent,
        data
    ):

        figure = Figure(
            figsize=(5, 3),
            dpi=90
        )

        figure.patch.set_facecolor(WHITE)

        ax = figure.add_subplot(111)


        filtered = {
            key: value
            for key, value in data.items()
            if value > 0
        }


        if not filtered:

            ax.text(
                0.5,
                0.5,
                "No inventory data",
                ha="center",
                va="center",
                fontsize=12
            )

            ax.axis("off")

        else:

            labels = list(
                filtered.keys()
            )

            values = list(
                filtered.values()
            )


            ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={
                    "fontsize": 8
                }
            )


            ax.set_title(
                "Stock Distribution",
                fontsize=11,
                pad=8
            )


        figure.tight_layout()


        canvas = FigureCanvasTkAgg(
            figure,
            master=parent
        )

        canvas.draw()


        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )


    # ========================================================
    # CHART 3
    # STOCK VALUE BY CATEGORY
    # ========================================================

    def create_category_value_chart(
        self,
        parent,
        data
    ):

        figure = Figure(
            figsize=(5, 3),
            dpi=90
        )

        figure.patch.set_facecolor(WHITE)

        ax = figure.add_subplot(111)

        ax.set_facecolor(WHITE)


        if not data:

            ax.text(
                0.5,
                0.5,
                "No inventory data",
                ha="center",
                va="center",
                fontsize=12
            )

            ax.axis("off")

        else:

            categories = list(
                data.keys()
            )

            values = list(
                data.values()
            )


            bars = ax.bar(
                categories,
                values
            )


            ax.set_ylabel(
                "Value (₹)",
                fontsize=9
            )


            ax.tick_params(
                axis="x",
                rotation=25,
                labelsize=8
            )

            ax.tick_params(
                axis="y",
                labelsize=8
            )


            ax.grid(
                axis="y",
                alpha=0.2
            )


            ax.set_axisbelow(True)


            ax.spines["top"].set_visible(False)

            ax.spines["right"].set_visible(False)


            # Add values

            for bar, value in zip(
                bars,
                values
            ):

                if value >= 100000:

                    display_value = (
                        f"₹{value / 100000:.1f}L"
                    )

                elif value >= 1000:

                    display_value = (
                        f"₹{value / 1000:.1f}K"
                    )

                else:

                    display_value = (
                        f"₹{value:.0f}"
                    )


                ax.text(
                    bar.get_x()
                    + bar.get_width() / 2,
                    bar.get_height(),
                    display_value,
                    ha="center",
                    va="bottom",
                    fontsize=8
                )


        figure.tight_layout()


        canvas = FigureCanvasTkAgg(
            figure,
            master=parent
        )

        canvas.draw()


        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )


    # ========================================================
    # CHART 4
    # STOCK STATUS
    # ========================================================

    def create_stock_status_chart(
        self,
        parent,
        data
    ):

        figure = Figure(
            figsize=(5, 3),
            dpi=90
        )

        figure.patch.set_facecolor(WHITE)

        ax = figure.add_subplot(111)


        if not data:

            ax.text(
                0.5,
                0.5,
                "No inventory data",
                ha="center",
                va="center",
                fontsize=12
            )

            ax.axis("off")

        else:

            labels = list(
                data.keys()
            )

            values = list(
                data.values()
            )


            ax.pie(
                values,
                labels=labels,
                autopct="%1.0f%%",
                startangle=90,
                textprops={
                    "fontsize": 8
                }
            )


            ax.set_title(
                "Stock Status",
                fontsize=11,
                pad=8
            )


        figure.tight_layout()


        canvas = FigureCanvasTkAgg(
            figure,
            master=parent
        )

        canvas.draw()


        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
=======
            self.content,
            text=report,
            justify="left",
            font=ctk.CTkFont(
                size=17
            ),
            text_color=TEXT
        ).pack(
            anchor="w",
            pady=40
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


    # ========================================================
    # SETTINGS
    # ========================================================

    def show_settings(self):

        title = ctk.CTkLabel(
            self.content,
            text="Settings",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=TEXT
        )

        title.pack(
            anchor="w"
        )


        database_location = str(
<<<<<<< HEAD
            PROJECT_ROOT
            / "Database"
            / "inventory.db"
        )


        # ----------------------------------------------------
        # DATABASE CARD
        # ----------------------------------------------------

        card = ctk.CTkFrame(
            self.content,
            fg_color=WHITE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )

        card.pack(
            fill="x",
            pady=(30, 0)
=======
            PROJECT_ROOT / "Database" / "inventory.db"
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


        ctk.CTkLabel(
<<<<<<< HEAD
            card,
=======
            self.content,
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
            text="Database",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color=TEXT
        ).pack(
            anchor="w",
<<<<<<< HEAD
            padx=25,
            pady=(25, 5)
=======
            pady=(40, 5)
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


        ctk.CTkLabel(
<<<<<<< HEAD
            card,
            text=database_location,
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=25
=======
            self.content,
            text=database_location,
            text_color=MUTED
        ).pack(
            anchor="w"
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


        ctk.CTkLabel(
<<<<<<< HEAD
            card,
            text="● Database Status: Connected",
            text_color=GREEN,
            font=ctk.CTkFont(
                size=14,
=======
            self.content,
            text="Database Status: Connected",
            text_color=GREEN,
            font=ctk.CTkFont(
                size=15,
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
                weight="bold"
            )
        ).pack(
            anchor="w",
<<<<<<< HEAD
            padx=25,
            pady=(15, 25)
=======
            pady=20
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


    # ========================================================
    # CREATE INVOICE
    # ========================================================

    def create_invoice(self):

        messagebox.showinfo(
            "Create Invoice",
<<<<<<< HEAD
            "Billing and invoice generation will be added "
            "in the next module."
=======
            "Billing and invoice generation will be added in the next module."
>>>>>>> 779de1229d827f475d12f469a0331bd99890aa75
        )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app = DashboardApp()

    app.mainloop()