import csv
import matplotlib.pyplot as plt
from datetime import datetime

# =====================================================
# PRODUCT CLASS
# =====================================================
class Product:
    def __init__(self, product_id, name, category, price, quantity, reorder_level):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity
        self.reorder_level = reorder_level

    def update_quantity(self, amount):
        self.quantity += amount

    def is_low_stock(self):
        return self.quantity <= self.reorder_level


# =====================================================
# INVENTORY CLASS (DICTIONARY STORAGE)
# =====================================================
class Inventory:
    def __init__(self):
        self.products = {}   # product_id -> Product

    def add_product(self, product):
        self.products[product.product_id] = product
        self.check_low_stock(product)

    def remove_product(self, product_id):
        self.products.pop(product_id, None)

    def get_product(self, product_id):
        return self.products.get(product_id)

    def search_by_name(self, name):
        return [p for p in self.products.values() if name.lower() in p.name.lower()]

    def search_by_category(self, category):
        return [p for p in self.products.values() if p.category.lower() == category.lower()]

    def list_products(self):
        print("***********************************************************************")
        print("\t \t \t INVENTORY STOCK")
        print("***********************************************************************")
        print("\nID | Name | Category | Price | Qty | Reorder")
        for p in self.products.values():
            alert = " ⚠️" if p.is_low_stock() else ""
            print(f"{p.product_id} | {p.name} | {p.category} | {p.price} | {p.quantity} | {p.reorder_level}{alert}")

    def check_low_stock(self, product):
        if product.is_low_stock():
            print(f"⚠️ LOW STOCK ALERT: {product.name} ({product.quantity} left)")


# =====================================================
# FILE MANAGER (CSV IMPORT / EXPORT)
# =====================================================
class FileManager:
    @staticmethod
    def save_inventory(inventory, inventory_products):
        with open(inventory_products, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "product_id", "name", "category",
                "price", "quantity", "reorder_level"
            ])
            for p in inventory.products.values():
                writer.writerow([
                    p.product_id, p.name, p.category,
                    p.price, p.quantity, p.reorder_level
                ])

    @staticmethod
    def load_inventory(inventory_products):
        inventory = Inventory()
        with open(inventory_products, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                product = Product(
                    int(row["product_id"]),
                    row["name"],
                    row["category"],
                    float(row["price"]),
                    int(row["quantity"]),
                    int(row["reorder_level"])
                )
                inventory.add_product(product)
        return inventory


# =====================================================
# TRANSACTION LOGGING
# =====================================================
class Transaction:
    def __init__(self, transaction_id, product_id, quantity, transaction_type):
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.quantity = quantity
        self.transaction_type = transaction_type
        self.date = datetime.now()


class TransactionLogger:
    def __init__(self):
        self.transactions = []

    def log(self, transaction):
        self.transactions.append(transaction)


# =====================================================
# STATISTICAL REPORTS
# =====================================================
class StatisticalReport:
    def __init__(self, inventory, logger):
        self.inventory = inventory
        self.logger = logger

    def total_inventory_value(self):
        print("***********************************************")
        total = sum(p.price * p.quantity for p in self.inventory.products.values())
        print(f"💰 Total Inventory Value: {total}")
        print("***********************************************\n")
        return total

    def turnover_report(self):
        print("\n************************************************")
        print("\t 📊 TURNOVER REPORT")
        print("************************************************")
        turnover = {}
        for t in self.logger.transactions:
            if t.transaction_type == "OUT":
                turnover[t.product_id] = turnover.get(t.product_id, 0) + abs(t.quantity)

        for pid, product in self.inventory.products.items():
            print(f"{product.name}: {turnover.get(pid, 0)} units sold")


# =====================================================
# DATA VISUALIZATION
# =====================================================
class Visualizer:
    @staticmethod
    def plot_inventory(inventory):
        names = [p.name for p in inventory.products.values()]
        quantities = [p.quantity for p in inventory.products.values()]

        plt.bar(names, quantities)
        plt.xlabel("Products")
        plt.ylabel("Quantity")
        plt.title("Inventory Levels")
        plt.xticks(rotation=45)
        plt.show()


# =====================================================
# MENU-DRIVEN INTERFACE
# =====================================================
class Menu:
    def __init__(self):
        self.inventory = Inventory()
        self.logger = TransactionLogger()

    def display(self):
        print("""
--- INVENTORY MANAGEMENT SYSTEM ---
1. Add product
2. Remove product
3. List products
4. Search by name
5. Search by category
6. Update quantity
7. Show inventory chart
8. Save to CSV
9. Load low stocks from CSV
10. Statistical reports
0. Exit
""")

    def run(self):
        while True:
            self.display()
            choice = input("Choice: ")

            if choice == "1":
                p = Product(
                    int(input("ID: ")),
                    input("Name: "),
                    input("Category: "),
                    float(input("Price: ")),
                    int(input("Quantity: ")),
                    int(input("Reorder level: "))
                )
                self.inventory.add_product(p)

            elif choice == "2":
                self.inventory.remove_product(int(input("Product ID: ")))

            elif choice == "3":
                self.inventory.list_products()

            elif choice == "4":
                for p in self.inventory.search_by_name(input("Name: ")):
                    print(p.name, p.quantity)

            elif choice == "5":
                for p in self.inventory.search_by_category(input("Category: ")):
                    print(p.name, p.quantity)

            elif choice == "6":
                pid = int(input("Product ID: "))
                qty = int(input("Quantity (+/-): "))
                product = self.inventory.get_product(pid)
                if product:
                    product.update_quantity(qty)
                    ttype = "IN" if qty > 0 else "OUT"
                    self.logger.log(Transaction(len(self.logger.transactions)+1, pid, qty, ttype))
                    self.inventory.check_low_stock(product)

            elif choice == "7":
                Visualizer.plot_inventory(self.inventory)

            elif choice == "8":
                FileManager.save_inventory(self.inventory, input("CSV filename: "))
                print("Saved successfully.")

            elif choice == "9":
                self.inventory = FileManager.load_inventory(input("CSV filename: "))
                print("Loaded successfully.")

            elif choice == "10":
                report = StatisticalReport(self.inventory, self.logger)
                report.total_inventory_value()
                report.turnover_report()

            elif choice == "0":
                print("Exiting system.")
                break

            else:
                print("Invalid choice.")


# =====================================================
# PROGRAM ENTRY POINT
# =====================================================
if __name__ == "__main__":
    Menu().run()
