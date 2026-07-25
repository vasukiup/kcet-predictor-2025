"""
Let's print the entire text of page 138 and 139 to see why there is a mismatch.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    print("=== PAGE 138 ===")
    print(pdf.pages[137].extract_text()[:4000])
    print("\n=== PAGE 139 ===")
    print(pdf.pages[138].extract_text()[:4000])
