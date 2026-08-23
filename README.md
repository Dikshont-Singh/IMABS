# IMABS — Inventory Management & Billing System

A desktop-based inventory management system built with **Python**, **CustomTkinter**, and **SQLite**.

IMABS helps manage products, stock levels, CSV data, inventory reports, and basic billing operations through a simple graphical interface.

---

## ✨ Features

- 📊 Dashboard with inventory statistics
- 📦 Add, edit, and delete products
- 🔍 Search products
- 📥 Import products from CSV
- 📤 Export inventory to CSV
- 🗄️ SQLite database
- 📈 Inventory reports and charts
- ⚠️ Low-stock and out-of-stock tracking
- 🧾 Billing module
- 🎨 Clean CustomTkinter interface
- 🖥️ Windows `.exe` support using PyInstaller

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CustomTkinter | Graphical User Interface |
| SQLite | Database |
| Matplotlib | Reports and graphs |
| CSV | Import/export inventory data |
| PyInstaller | Convert Python project into `.exe` |

---

## 📁 Project Structure

```text
IMABS/
│
├── main.py
├── database.py
├── IMABS.ico
├── README.md
│
├── Database/
│   └── inventory.db
│
└── dist/
    └── IMABS/
        └── IMABS.exe
