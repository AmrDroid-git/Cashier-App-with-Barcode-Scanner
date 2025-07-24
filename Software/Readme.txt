main.py – launcher

db.sqlite – product and sales database

database.py – handles all DB operations

main_window.py – main UI with tabs

products_tab.py – manage product list (add/edit/delete)

operation_tab.py – scan, calculate total, generate facture

pdf_generator.py – makes PDF facture

history_tab.py – view past sales and factures



final step is to build the software(become .exe file):
pyinstaller --clean --onefile --windowed --icon=assets/icon.ico --add-data "style.qss;." --add-data "assets/icon.ico;assets" main.py