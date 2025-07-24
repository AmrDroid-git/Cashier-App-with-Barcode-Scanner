from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, 
                            QInputDialog, QMessageBox)

from services.database import get_cart_items, get_product_by_barcode, get_connection, clear_cart


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
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make table read-only
        self.table.verticalHeader().setVisible(False)  # Hide row numbers
        self.layout.addWidget(self.table)
        
        # Total label
        self.total_label = QLabel("Total: 0.0")
        self.layout.addWidget(self.total_label)
        
        # Finish button
        self.finish_btn = QPushButton("Finish Scanning")
        self.finish_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.finish_btn)
        
        # Delete button
        self.delete_btn = QPushButton("Delete Selected Item")
        self.delete_btn.clicked.connect(self.delete_selected_item)
        self.layout.addWidget(self.delete_btn)
        
        # Update quantity button
        self.update_qty_btn = QPushButton("Update Quantity")
        self.update_qty_btn.clicked.connect(self.update_quantity)
        self.layout.addWidget(self.update_qty_btn)
        
        # Cancel scan button
        self.cancel_btn = QPushButton("Cancel Scan")
        self.cancel_btn.clicked.connect(self.cancel_scan)
        self.layout.addWidget(self.cancel_btn)
        
        # Initialize cart
        self.cart = []

    def add_product(self, product):
        # product: (id, name, barcode, price, quantity)
    
        # Check if product already exists in cart
        for i, item in enumerate(self.cart):
            if item[2] == product[2]:  # Compare barcodes
                # Update quantity
                new_quantity = item[4] + 1
                self.cart[i] = (item[0], item[1], item[2], item[3], new_quantity)
                self.update_table()
                print(f"Updated quantity for {product[1]} to {new_quantity}")
                return
    
        # If not found, add new product with quantity 1
        product_with_quantity = (*product, 1)  # Add quantity=1 to the product tuple
        self.cart.append(product_with_quantity)
        self.update_table()
        print(f"Added new product: {product[1]} (Quantity: 1)")

    def update_table(self):
        """Update the table from the cart in database"""
        self.cart = []

        for row in get_cart_items():
            # row = (id, name, barcode, price, quantity_to_buy)
            cart_id, name, barcode, price, quantity = row
            self.cart.append((cart_id, name, barcode, price, quantity))

        self.table.setRowCount(len(self.cart))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Barcode", "Price", "Quantity"])

        for row, product in enumerate(self.cart):
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))  # ID from cart
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))       # Name
            self.table.setItem(row, 2, QTableWidgetItem(product[2]))       # Barcode
            self.table.setItem(row, 3, QTableWidgetItem(f"{product[3]:.2f}"))  # Price
            self.table.setItem(row, 4, QTableWidgetItem(str(product[4])))  # Quantity

        total = sum(p[3] * p[4] for p in self.cart)
        self.total_label.setText(f"Total: {total:.2f}")

    def delete_selected_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            return  # No row selected

        barcode = self.cart[selected][2]  # barcode is at index 2
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

        available_stock = product[4]  # quantity in product table
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
        self.reject()  # Close the dialog
