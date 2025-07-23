🧾 Cashier App with Barcode Scanner

This project is a complete cashier system designed for small to medium-sized shops. It includes:

📱 Android App (APK): Scan product barcodes using a mobile device. Automatically fetch product info and send it to the Windows software.

💻 Windows Software: Acts as the central cashier interface. Displays scanned products, calculates totals, applies discounts, and prints receipts.

🗄️ Database (Local or Networked): Stores product info (name, price, barcode), transaction history, stock levels, and more.

🔧 Features

- Real-time barcode scanning and product lookup
- Product management (add/edit/delete products)
- Cart system with live total and receipt generation
- Sales history tracking
- Sync between Android device and Windows app (via Wi-Fi or local network)
- Easy-to-use interface for both mobile and desktop
- Optional admin login for restricted actions

📦 Tech Stack

- Android App: Kotlin + Jetpack Compose + CameraX (for scanning)
- Windows App: Python (Tkinter or PyQt) / C# (WPF) [depending on version]
- Database: SQLite or MySQL (with local or networked option)
- Communication: REST API / Socket / QR sync [planned]
