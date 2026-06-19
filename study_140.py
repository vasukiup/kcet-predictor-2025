"""
Print page 140 (index 139) to check the bottom of college #19 and top of college #20.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("Seat_Matrix_05072025.pdf", "rb") as f:
    pdf = pdfplumber.open(f)
    print("=== PAGE 140 ===")
    print(pdf.pages[139].extract_text()[:4000])
