import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in [12, 13, 14, 15]:
        page = pdf.pages[pg_num - 1]
        text = page.extract_text()
        print(f"\n{'='*70}")
        print(f"PAGE {pg_num}")
        print('='*70)
        if text:
            print(text)
        else:
            print("(no text layer - image page)")
