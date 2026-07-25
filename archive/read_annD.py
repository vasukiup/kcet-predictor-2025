"""
Read all Annexure D pages (94-101) to extract the correct 16 minority colleges.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in range(94, 103):
        page = pdf.pages[pg_num - 1]
        text = page.extract_text()
        print(f"\n{'='*72}")
        print(f"PAGE {pg_num}")
        print('='*72)
        if text:
            print(text)
        else:
            print("(no text layer)")
