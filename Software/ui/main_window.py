from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.products_tab import ProductsTab
from ui.operation_tab import OperationTab
from ui.history_tab import HistoryTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barcode Master")
        self.setGeometry(100, 100, 800, 600)

        tabs = QTabWidget()
        tabs.addTab(ProductsTab(), "Products")
        tabs.addTab(OperationTab(), "Buy / Operation")
        tabs.addTab(HistoryTab(), "History")

        self.setCentralWidget(tabs)
