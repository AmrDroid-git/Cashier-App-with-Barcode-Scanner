from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.products_tab import ProductsTab
from ui.operation_tab import OperationTab
from ui.history_tab import HistoryTab
from PyQt6.QtGui import QIcon
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barcode Master")
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()

        # Store instances so we can refresh them later
        self.products_tab = ProductsTab()
        self.operation_tab = OperationTab()
        self.history_tab = HistoryTab()

        self.tabs.addTab(self.products_tab, "Products")
        self.tabs.addTab(self.operation_tab, "Buy / Operation")
        self.tabs.addTab(self.history_tab, "History")

        self.setCentralWidget(self.tabs)

        # Connect tab switch to refresh
        self.tabs.currentChanged.connect(self.refresh_tab)

    def refresh_tab(self, index):
        if index == 0:  # Products
            self.products_tab.load_products()
        elif index == 1:  # Operation
            if self.operation_tab.scan_window:
                self.operation_tab.scan_window.update_table()
        elif index == 2:  # History
            self.history_tab.load_history()
