from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from ui.start_scan_window import ScanningWindow
from services.database import (
    get_product_by_barcode, clear_cart,
    add_to_cart_or_increment
)
import subprocess

class OperationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.scan_btn = QPushButton("Start Scanning")
        self.scan_btn.clicked.connect(self.start_scanning)
        self.scan_btn.setObjectName("start_scan")
        self.layout.addWidget(self.scan_btn)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_new_barcode)

        self.last_modified_time = None
        self.last_barcode = None
        self.scan_window = None

    def start_scanning(self):
        if not self.scan_window or not self.scan_window.isVisible():
            self.scan_window = ScanningWindow()
            self.scan_window.show()

        clear_cart()
        self.scan_window.update_table()
        self.last_modified_time = self.get_barcode_file_mtime()
        self.last_barcode = None
        self.timer.start()

    def silent_subprocess(self, command_list):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.check_output(command_list, startupinfo=startupinfo)

    def get_barcode_file_mtime(self):
        try:
            result = self.silent_subprocess(
                ['adb', 'shell', 'stat', '-c', '%Y', '/sdcard/barcode.txt']
            )
            return float(result.decode().strip())
        except Exception:
            return None

    def get_last_barcode(self):
        try:
            result = self.silent_subprocess(
                ['adb', 'shell', 'tail', '-n', '1', '/sdcard/barcode.txt']
            )
            full_line = result.decode().strip()
            barcode = full_line.split('|')[0].strip()
            return barcode
        except Exception:
            return None

    def check_new_barcode(self):
        current_mtime = self.get_barcode_file_mtime()
        if current_mtime and (self.last_modified_time is None or current_mtime > self.last_modified_time):
            self.last_modified_time = current_mtime
            barcode = self.get_last_barcode()
            if barcode:
                product = get_product_by_barcode(barcode)
                if product is None:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("This product does not exist in the database.")
                    msg.setWindowTitle("Product Not Found")
                    msg.exec()
                    return
                try:
                    add_to_cart_or_increment(barcode)
                except ValueError as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(str(e))
                    msg.setWindowTitle("Stock Error")
                    msg.exec()
                    return
                if self.scan_window:
                    self.scan_window.update_table()

    def finish_operation(self):
        if self.scan_window:
            self.scan_window.close()
        self.timer.stop()
