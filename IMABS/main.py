import customtkinter as ctk

# -------------------- Appearance --------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# -------------------- Window --------------------
app = ctk.CTk()
app.title("Inventory Management System")
app.geometry("1400x800")

# -------------------- Colors --------------------
SIDEBAR = "#172554"
BG = "#F8FAFC"
CARD = "#FFFFFF"
PRIMARY = "#2563EB"

app.configure(fg_color=BG)

# ================= Sidebar =================

sidebar = ctk.CTkFrame(
    app,
    width=220,
    corner_radius=0,
    fg_color=SIDEBAR
)
sidebar.pack(side="left", fill="y")

logo = ctk.CTkLabel(
    sidebar,
    text="IMABS",
    font=("Segoe UI", 24, "bold"),
    text_color="white"
)
logo.pack(pady=(30,40))

menu = [
    "Dashboard",
    "Inventory",
    "Billing",
    "Reports",
    "Settings"
]

for item in menu:
    btn = ctk.CTkButton(
        sidebar,
        text=item,
        width=170,
        height=40,
        fg_color="transparent",
        hover_color="#1E3A8A",
        anchor="w"
    )
    btn.pack(pady=5)

# ================= Main Area =================

main = ctk.CTkFrame(
    app,
    fg_color=BG,
    corner_radius=0
)
main.pack(side="left", fill="both", expand=True)

# ================= Top Bar =================

top = ctk.CTkFrame(
    main,
    fg_color="transparent",
    height=70
)
top.pack(fill="x", padx=25, pady=20)

search = ctk.CTkEntry(
    top,
    width=350,
    placeholder_text="Search inventory..."
)
search.pack(side="left")

invoice = ctk.CTkButton(
    top,
    text="+ Create Invoice",
    fg_color=PRIMARY
)
invoice.pack(side="right")

# ================= Title =================

title = ctk.CTkLabel(
    main,
    text="Overview",
    font=("Segoe UI",32,"bold"),
    text_color="#0F172A"
)
title.pack(anchor="w", padx=25)

# ================= Cards =================

cards = ctk.CTkFrame(
    main,
    fg_color="transparent"
)
cards.pack(fill="x", padx=20, pady=20)

data = [
    ("Total Stock Value", "$42,850"),
    ("Low Stock", "12 Items"),
    ("Today's Sales", "$3,150"),
    ("Outstanding", "8 Bills")
]

for title, value in data:

    card = ctk.CTkFrame(
        cards,
        width=250,
        height=120,
        fg_color=CARD,
        corner_radius=12
    )

    card.pack(side="left", padx=10)
    card.pack_propagate(False)

    ctk.CTkLabel(
        card,
        text=title,
        font=("Segoe UI",13)
    ).pack(anchor="w", padx=20, pady=(15,5))

    ctk.CTkLabel(
        card,
        text=value,
        font=("Segoe UI",28,"bold")
    ).pack(anchor="w", padx=20)

# ================= Inventory Table Placeholder =================

table = ctk.CTkFrame(
    main,
    fg_color=CARD,
    corner_radius=12
)

table.pack(fill="both", expand=True, padx=25, pady=10)

ctk.CTkLabel(
    table,
    text="Inventory Table",
    font=("Segoe UI",22,"bold")
).pack(pady=30)

app.mainloop()