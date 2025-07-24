from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import QTimer
from ui.start_scan_window import ScanningWindow
from services.database import get_product_by_barcode
from services.database import get_product_by_barcode, clear_cart, add_to_cart_or_increment, get_cart_items
import subprocess
from PyQt6.QtWidgets import QMessageBox
import os


class OperationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Scan button
        self.scan_btn = QPushButton("Start Scanning")
        self.scan_btn.clicked.connect(self.start_scanning)
        self.scan_btn.setObjectName("start_scan")
        self.layout.addWidget(self.scan_btn)
        
        # Setup timer
        self.timer = QTimer()
        self.timer.setInterval(1000)  # Check every second
        self.timer.timeout.connect(self.check_new_barcode)
        
        # Tracking variables
        self.last_modified_time = None
        self.last_barcode = None
        self.scan_window = None

    def start_scanning(self):
        if not self.scan_window or not self.scan_window.isVisible():
            self.scan_window = ScanningWindow()
            self.scan_window.show()

        clear_cart()  # Clear cart table
        self.scan_window.update_table()
        self.last_modified_time = self.get_barcode_file_mtime()
        self.last_barcode = None
        self.timer.start()
        print("Scanning started...")


    def get_barcode_file_mtime(self):
        """Get last modified time of barcode file"""
        try:
            result = subprocess.check_output(
                ['adb', 'shell', 'stat', '-c', '%Y', '/sdcard/barcode.txt']
            )
            return float(result.decode().strip())
        except Exception as e:
            print(f"Error getting file mtime: {e}")
            return None

    def get_last_barcode(self):
        """Get the most recent barcode from file (extracts just the barcode part)"""
        try:
            # Get the last line from the file
            result = subprocess.check_output(
                ['adb', 'shell', 'tail', '-n', '1', '/sdcard/barcode.txt']
            )
            full_line = result.decode().strip()
        
            # Split the line and take just the barcode part (before the |)
            barcode = full_line.split('|')[0].strip()
            return barcode
        
        except Exception as e:
            print(f"Error reading barcode: {e}")
            return None

    def check_new_barcode(self):
        """Check for new barcodes and add to cart"""
        current_mtime = self.get_barcode_file_mtime()
        
        # Only proceed if we have a valid time and the file has changed
        if current_mtime and (self.last_modified_time is None or 
                            current_mtime > self.last_modified_time):
            self.last_modified_time = current_mtime
            barcode = self.get_last_barcode()
            
            # Only process if we have a new barcode
            if barcode:
                product = get_product_by_barcode(barcode)
                
                if product is None:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("This product does not exist in the database.")
                    msg.setWindowTitle("Product Not Found")
                    msg.exec()
                    return
                
                # Product exists: add to cart and update table
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
        """Clean up when scanning is complete"""
        if self.scan_window:
            self.scan_window.close()
        self.timer.stop()
        print("Scanning stopped")