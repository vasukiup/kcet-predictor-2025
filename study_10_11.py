"""
Print page 10 (index 9) and page 11 (index 10) in full to see college #22CPGS Kalaburgi and college #23.
"""
import pdfplumber

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

print("=== Page 10 ===")
print(pdf.pages[9].extract_text())

print("\n=== Page 11 ===")
print(pdf.pages[10].extract_text())
