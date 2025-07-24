from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, 
                            QInputDialog, QMessageBox, QFileDialog)

from services.database import get_cart_items, get_product_by_barcode, get_connection, clear_cart, record_sale, record_facture, add_to_cart_or_increment, decrement_stock_after_sale
from services.pdf_generator import generate_facture_pdf
from datetime import datetime


class ScanningWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scanning Products")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout(self)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Barcode", "Price"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)
        
        # Total label
        self.total_label = QLabel("Total: 0.0")
        self.layout.addWidget(self.total_label)
        
        # Buttons
        self.finish_btn = QPushButton("Finish Scanning")
        self.finish_btn.clicked.connect(self.confirm_and_generate_pdf)
        self.layout.addWidget(self.finish_btn)
        
        self.delete_btn = QPushButton("Delete Selected Item")
        self.delete_btn.clicked.connect(self.delete_selected_item)
        self.layout.addWidget(self.delete_btn)
        
        self.update_qty_btn = QPushButton("Update Quantity")
        self.update_qty_btn.clicked.connect(self.update_quantity)
        self.layout.addWidget(self.update_qty_btn)
        
        self.add_barcode_btn = QPushButton("Add Product with Barcode")
        self.add_barcode_btn.clicked.connect(self.add_product_manually)
        self.layout.addWidget(self.add_barcode_btn)
        
        self.cancel_btn = QPushButton("Cancel Scan")
        self.cancel_btn.clicked.connect(self.cancel_scan)
        self.layout.addWidget(self.cancel_btn)
        
        self.cart = []

    def add_product(self, product):
        for i, item in enumerate(self.cart):
            if item[2] == product[2]:
                new_quantity = item[4] + 1
                self.cart[i] = (item[0], item[1], item[2], item[3], new_quantity)
                self.update_table()
                print(f"Updated quantity for {product[1]} to {new_quantity}")
                return
        product_with_quantity = (*product, 1)
        self.cart.append(product_with_quantity)
        self.update_table()
        print(f"Added new product: {product[1]} (Quantity: 1)")

    def update_table(self):
        self.cart = []
        for row in get_cart_items():
            cart_id, name, barcode, price, quantity = row
            self.cart.append((cart_id, name, barcode, price, quantity))

        self.table.setRowCount(len(self.cart))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Barcode", "Price", "Quantity"])

        for row, product in enumerate(self.cart):
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.table.setItem(row, 2, QTableWidgetItem(product[2]))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product[3]:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(product[4])))

        total = sum(p[3] * p[4] for p in self.cart)
        self.total_label.setText(f"Total: {total:.2f}")

    def delete_selected_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        barcode = self.cart[selected][2]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM cart WHERE barcode = ?", (barcode,))
        conn.commit()
        conn.close()
        self.update_table()

    def update_quantity(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        barcode = self.cart[selected][2]
        product = get_product_by_barcode(barcode)
        if not product:
            return

        available_stock = product[4]
        qty, ok = QInputDialog.getInt(self, "Update Quantity", "Enter new quantity:", min=1)

        if ok:
            if qty > available_stock:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(f"Only {available_stock} items available in stock.")
                msg.setWindowTitle("Stock Error")
                msg.exec()
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE cart SET quantity_to_buy = ? WHERE barcode = ?", (qty, barcode))
            conn.commit()
            conn.close()
            self.update_table()

    def cancel_scan(self):
        clear_cart()
        self.update_table()
        self.reject()

    def confirm_and_generate_pdf(self):
        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to finish and generate the facture?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save Facture")
        if not folder_path:
            return

        items = get_cart_items()
        if not items:
            QMessageBox.information(self, "Empty Cart", "No products to save.")
            return

        formatted_items = [(name, barcode, price, quantity) for _, name, barcode, price, quantity in items]
        operation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        filepath = generate_facture_pdf(operation_id, formatted_items, folder_path)

        # Record sales
        for _, name, barcode, price, quantity in items:
            record_sale(barcode, name, price, quantity)
            
        # Decrement stock
        decrement_stock_after_sale(items)

        # Record facture
        total_price = sum(price * quantity for _, name, barcode, price, quantity in items)
        record_facture(total_price, filepath)

        QMessageBox.information(self, "Saved", f"Facture saved successfully:\n{filepath}")
        clear_cart()
        self.accept()

    def add_product_manually(self):
        barcode, ok = QInputDialog.getText(self, "Enter Barcode", "Type the barcode manually:")
        if ok and barcode:
            product = get_product_by_barcode(barcode.strip())
            if not product:
                QMessageBox.warning(self, "Not Found", "Product not found in database.")
                return

            available_qty = product[4]
            if available_qty <= 0:
                QMessageBox.warning(self, "Out of Stock", "This product is out of stock.")
                return

            try:
                add_to_cart_or_increment(barcode.strip())
            except ValueError as e:
                QMessageBox.warning(self, "Stock Error", str(e))
                return

            self.update_table()
