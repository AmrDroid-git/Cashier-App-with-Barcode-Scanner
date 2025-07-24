from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QMessageBox, QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt
from services.database import (
    get_sales_history,
    get_facture_history,
    cancel_sale,
    delete_facture_by_path
)
from services.table_to_pdf import generate_table_pdf


class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Export buttons
        self.sales_export_btn = QPushButton("Export Sales to PDF")
        self.sales_export_btn.clicked.connect(self.export_sales_to_pdf)
        layout.addWidget(self.sales_export_btn)

        layout.addWidget(QLabel("Sales History"))

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Barcode", "Name", "Price", "Qty", "Date"])
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.sales_table)

        self.facture_export_btn = QPushButton("Export Factures to PDF")
        self.facture_export_btn.clicked.connect(self.export_factures_to_pdf)
        layout.addWidget(self.facture_export_btn)

        layout.addWidget(QLabel("Facture History"))

        self.facture_table = QTableWidget()
        self.facture_table.setColumnCount(3)
        self.facture_table.setHorizontalHeaderLabels(["Total", "Date", "File"])
        self.facture_table.verticalHeader().setVisible(False)
        self.facture_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.facture_table)

        # Control buttons
        self.cancel_btn = QPushButton("Cancel Selected Sale")
        self.cancel_btn.clicked.connect(self.cancel_selected_sale)
        layout.addWidget(self.cancel_btn)

        self.delete_facture_btn = QPushButton("Delete Selected Facture")
        self.delete_facture_btn.clicked.connect(self.delete_selected_facture)
        layout.addWidget(self.delete_facture_btn)

        self.load_history()

    def load_history(self):
        sales = get_sales_history()
        self.sales_table.setRowCount(0)
        for row_idx, sale in enumerate(sales):
            self.sales_table.insertRow(row_idx)
            for col_idx, value in enumerate(sale[1:]):
                self.sales_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        factures = get_facture_history()
        self.facture_table.setRowCount(0)
        for row_idx, f in enumerate(factures):
            self.facture_table.insertRow(row_idx)
            for col_idx, value in enumerate(f[1:]):
                self.facture_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def cancel_selected_sale(self):
        selected_row = self.sales_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a sale to cancel.")
            return

        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to cancel this sale?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        barcode = self.sales_table.item(selected_row, 0).text()
        name = self.sales_table.item(selected_row, 1).text()
        price = float(self.sales_table.item(selected_row, 2).text())
        quantity = int(self.sales_table.item(selected_row, 3).text())
        date = self.sales_table.item(selected_row, 4).text()

        try:
            cancel_sale(barcode, quantity, date)
            QMessageBox.information(self, "Canceled", f"Sale for '{name}' was canceled.")
            self.load_history()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_facture(self):
        selected_row = self.facture_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a facture to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to delete this facture from the database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        file_path = self.facture_table.item(selected_row, 2).text()

        try:
            delete_facture_by_path(file_path)
            QMessageBox.information(self, "Deleted", f"Facture deleted from database:\n{file_path}")
            self.load_history()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete facture:\n{str(e)}")

    def export_sales_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Sales PDF", "", "PDF Files (*.pdf)")
        if path:
            rows = []
            for r in range(self.sales_table.rowCount()):
                row = [self.sales_table.item(r, c).text() for c in range(self.sales_table.columnCount())]
                rows.append(row)
            generate_table_pdf("Sales History", ["Barcode", "Name", "Price", "Qty", "Date"], rows, path)
            QMessageBox.information(self, "Saved", f"Sales exported to:\n{path}")

    def export_factures_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Factures PDF", "", "PDF Files (*.pdf)")
        if path:
            rows = []
            for r in range(self.facture_table.rowCount()):
                row = [self.facture_table.item(r, c).text() for c in range(self.facture_table.columnCount())]
                rows.append(row)
            generate_table_pdf("Facture History", ["Total", "Date", "File"], rows, path)
            QMessageBox.information(self, "Saved", f"Factures exported to:\n{path}")
