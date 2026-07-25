"""
Inspect the first few pages of Annexure E and V to see the column layout and row formats.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    # Let's print the first 2 pages of E (122, 123) and first 2 pages of V (325, 326)
    print("=== ANNEXURE E Page 122 ===")
    print(pdf.pages[121].extract_text()[:3000])
    print("\n=== ANNEXURE E Page 123 ===")
    print(pdf.pages[122].extract_text()[:3000])
    print("\n=== ANNEXURE V Page 325 ===")
    print(pdf.pages[324].extract_text()[:3000])
    print("\n=== ANNEXURE V Page 326 ===")
    print(pdf.pages[325].extract_text()[:3000])
