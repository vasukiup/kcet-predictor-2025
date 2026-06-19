"""
Check if there are pages after page 360 in the entire PDF.
"""
import pdfplumber
pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")
print("Total pages in PDF:", len(pdf.pages))
for i in range(360, len(pdf.pages)):
    print(f"--- Page {i+1} ---")
    print(pdf.pages[i].extract_text()[:500])
