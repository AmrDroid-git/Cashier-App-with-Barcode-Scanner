from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from services.database import get_sales_history, get_facture_history

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Sales History"))
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Barcode", "Name", "Price", "Qty", "Date"])
        layout.addWidget(self.sales_table)

        layout.addWidget(QLabel("Facture History"))
        self.facture_table = QTableWidget()
        self.facture_table.setColumnCount(3)
        self.facture_table.setHorizontalHeaderLabels(["Total", "Date", "File"])
        layout.addWidget(self.facture_table)

        self.load_history()

    def load_history(self):
        sales = get_sales_history()
        self.sales_table.setRowCount(0)
        for row, sale in enumerate(sales):
            self.sales_table.insertRow(row)
            for col, value in enumerate(sale[1:]):
                self.sales_table.setItem(row, col, QTableWidgetItem(str(value)))

        factures = get_facture_history()
        self.facture_table.setRowCount(0)
        for row, f in enumerate(factures):
            self.facture_table.insertRow(row)
            for col, value in enumerate(f[1:]):
                self.facture_table.setItem(row, col, QTableWidgetItem(str(value)))
