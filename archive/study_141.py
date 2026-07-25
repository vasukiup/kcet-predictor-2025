"""
Print the first 30 lines of page 141 (index 140) to see if college #20 starts there.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    print("=== PAGE 141 ===")
    print(pdf.pages[140].extract_text()[:2000])
