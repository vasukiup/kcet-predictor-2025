"""
Print page 148, 149, 150 to check headers and totals for colleges #25 and #26.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for pg in [148, 149, 150]:
    print(f"\n=== PAGE {pg} ===")
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines()[:15]:
        print(line.strip())
    print("...")
    for line in text.splitlines()[-10:]:
        print(line.strip())
