"""
Print page 10 and 11 of the PDF in full to see if VTU Belagavi Campus or another college is indeed college #23.
"""
import pdfplumber

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

print("=== Page 11 ===")
print(pdf.pages[10].extract_text()[:4000])

print("\n=== Page 12 ===")
print(pdf.pages[11].extract_text()[:4000])
