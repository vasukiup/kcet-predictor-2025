import pdfplumber
import re

PDF_PATH = "Seat_Matrix_05072025.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[85]  # Page 86 is index 85
    text = page.extract_text()
    lines = text.split("\n")
    
    # Let's print lines around Sri Venkateshwara College of Engineering
    found = False
    for idx, line in enumerate(lines):
        if "Sri Venkateshwara College of Engineering" in line or "134" in line:
            found = True
        if found:
            print(f"{idx}: {line}")
