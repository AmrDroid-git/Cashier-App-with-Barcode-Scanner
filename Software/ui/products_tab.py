from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox, QFileDialog
)
from services.database import (
    get_products, add_product, delete_product_by_barcode,
    update_product, get_product_by_barcode
)
from services.table_to_pdf import generate_table_pdf  # ✅ for PDF export


class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Barcode", "Price", "Quantity"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.load_selected_product)
        self.layout.addWidget(self.table)

        # Export button
        export_btn = QPushButton("Export Products to PDF")
        export_btn.clicked.connect(self.export_products_to_pdf)
        self.layout.addWidget(export_btn)

        # Input fields
        self.name_input = QLineEdit(placeholderText="Name")
        self.barcode_input = QLineEdit(placeholderText="Barcode")
        self.price_input = QLineEdit(placeholderText="Price")
        self.quantity_input = QLineEdit(placeholderText="Quantity")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.barcode_input)
        input_layout.addWidget(self.price_input)
        input_layout.addWidget(self.quantity_input)
        self.layout.addLayout(input_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        delete_btn = QPushButton("Delete")
        update_btn = QPushButton("Update")

        add_btn.clicked.connect(self.add_product)
        delete_btn.clicked.connect(self.delete_selected)
        update_btn.clicked.connect(self.update_selected)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(update_btn)
        self.layout.addLayout(btn_layout)

    def load_products(self):
        self.table.setRowCount(0)
        for row, product in enumerate(get_products()):
            self.table.insertRow(row)
            for col, value in enumerate(product):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def load_selected_product(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.name_input.setText(self.table.item(selected, 1).text())
            self.barcode_input.setText(self.table.item(selected, 2).text())
            self.price_input.setText(self.table.item(selected, 3).text())
            self.quantity_input.setText(self.table.item(selected, 4).text())

    def add_product(self):
        try:
            barcode = self.barcode_input.text().strip()
            if not all([self.name_input.text(), barcode, self.price_input.text(), self.quantity_input.text()]):
                raise ValueError("All fields are required")

            if get_product_by_barcode(barcode):
                raise ValueError(f"Product with barcode '{barcode}' already exists")

            add_product(
                self.name_input.text().strip(),
                barcode,
                float(self.price_input.text()),
                int(self.quantity_input.text())
            )
            self.load_products()
            self.clear_inputs()
            QMessageBox.information(self, "Success", "Product added successfully!")

        except ValueError as ve:
            QMessageBox.critical(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add product: {str(e)}")

    def delete_selected(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Missing Barcode", "Please enter a barcode to delete")
            return

        try:
            product = get_product_by_barcode(barcode)
            if not product:
                raise ValueError(f"No product found with barcode: {barcode}")

            reply = QMessageBox.question(
                self, 'Confirm Deletion',
                f"Delete product '{product[1]}' (Barcode: {barcode})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                delete_product_by_barcode(barcode)
                self.load_products()
                self.clear_inputs()
                QMessageBox.information(self, "Success", "Product deleted successfully!")

        except ValueError as ve:
            QMessageBox.critical(self, "Not Found", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")

    def update_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a product to update")
            return

        try:
            product_id = int(self.table.item(selected, 0).text())
            new_barcode = self.barcode_input.text().strip()
            original_barcode = self.table.item(selected, 2).text()

            if not all([self.name_input.text(), new_barcode, self.price_input.text(), self.quantity_input.text()]):
                raise ValueError("All fields are required")

            if new_barcode != original_barcode and get_product_by_barcode(new_barcode):
                raise ValueError(f"Barcode '{new_barcode}' already exists for another product")

            update_product(
                product_id,
                self.name_input.text().strip(),
                new_barcode,
                float(self.price_input.text()),
                int(self.quantity_input.text())
            )

            self.load_products()
            self.clear_inputs()
            QMessageBox.information(self, "Success", "Product updated successfully!")

        except ValueError as ve:
            QMessageBox.critical(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update product: {str(e)}")

    def export_products_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Product List", "", "PDF Files (*.pdf)")
        if not path:
            return

        try:
            rows = []
            for r in range(self.table.rowCount()):
                row = [self.table.item(r, c).text() for c in range(self.table.columnCount())]
                rows.append(row)

            generate_table_pdf("Product List", ["ID", "Name", "Barcode", "Price", "Quantity"], rows, path)
            QMessageBox.information(self, "Saved", f"Products exported to:\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export products:\n{str(e)}")

    def clear_inputs(self):
        self.name_input.clear()
        self.barcode_input.clear()
        self.price_input.clear()
        self.quantity_input.clear()
