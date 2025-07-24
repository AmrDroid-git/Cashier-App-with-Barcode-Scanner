from fpdf import FPDF
from datetime import datetime

def generate_table_pdf(title, headers, rows, filepath):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Generated: {timestamp}", ln=True, align='C')

    pdf.ln(5)

    # Set column widths based on title
    if title == "Facture History":
        col_widths = [30, 45, 115]  # Total, Date, File
    elif title == "Sales History":
        col_widths = [35, 30, 25, 20, 80]  # Barcode, Name, Price, Qty, Date
    else:
        col_widths = [pdf.w / len(headers)] * len(headers)  # fallback

    # Table headers
    pdf.set_font("Arial", "B", 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", "", 8)
    for row in rows:
        for i, item in enumerate(row):
            text = str(item)
            pdf.cell(col_widths[i], 6, text, border=1)
        pdf.ln()

    pdf.output(filepath)
