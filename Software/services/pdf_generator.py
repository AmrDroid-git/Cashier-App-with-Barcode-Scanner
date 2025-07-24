# services/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_facture_pdf(operation_id, scanned_items, output_path):
    filename = os.path.join(output_path, f"facture_{operation_id}.pdf")
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Barcode Master - Facture")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Facture ID: {operation_id}")
    c.drawString(50, height - 100, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Table headers
    headers = ["Name", "Barcode", "Price", "Quantity", "Total"]
    col_widths = [100, 120, 60, 60, 60]
    x_start = 50
    y = height - 140

    c.setFont("Helvetica-Bold", 11)
    for i, header in enumerate(headers):
        c.drawString(x_start + sum(col_widths[:i]), y, header)

    y -= 20
    total_price = 0

    c.setFont("Helvetica", 10)
    for item in scanned_items:
        name, barcode, price, quantity = item
        total = price * quantity
        total_price += total

        values = [name, barcode, f"{price:.2f}", str(quantity), f"{total:.2f}"]
        for i, value in enumerate(values):
            c.drawString(x_start + sum(col_widths[:i]), y, value)
        y -= 20
        if y < 100:  # Go to next page if needed
            c.showPage()
            y = height - 50

    # Total summary
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_start, y, f"Total to Pay: {total_price:.2f} TND")

    c.save()
    return filename
