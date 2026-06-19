"""
Check where the page numbers are in the PDF pages.
Let's print the bottom of page 138, 139, 140 to see what page numbers they say.
"""
import pdfplumber

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for idx in [137, 138, 139]:
    print(f"=== PAGE {idx+1} (Index {idx}) ===")
    lines = pdf.pages[idx].extract_text().splitlines()
    # print last 5 lines
    for l in lines[-5:]:
        print(l)
