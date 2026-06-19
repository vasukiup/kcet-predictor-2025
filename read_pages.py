"""
Extract raw text from pages 9-11 of the PDF to find the missing course
for college #21 (VTU VIAT Muddenahalli, Annexure A).
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in [9, 10, 11]:  # 1-indexed
        page = pdf.pages[pg_num - 1]
        text = page.extract_text()
        print(f"\n{'='*70}")
        print(f"PAGE {pg_num}")
        print('='*70)
        if text:
            print(text)
        else:
            print("(no text layer - image page)")
