import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.database import init_db

def main():
    init_db()  # ✅ Create tables before launching app

    app = QApplication(sys.argv)

    # ✅ Load and apply stylesheet
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ style.qss not found. Running without custom styles.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
