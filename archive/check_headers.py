"""
Let's print the column header of page 122 or page 123 to understand which column indices correspond to which headers.
"""
import pdfplumber

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")
page = pdf.pages[121]
print("=== CHARACTERS AND POSITIONS ON PAGE 122 ===")
text = page.extract_text()
lines = text.splitlines()
for line in lines[:5]:
    print(line)
