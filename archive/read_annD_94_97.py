import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in [94, 95, 96, 97]:
        page = pdf.pages[pg_num - 1]
        text = page.extract_text()
        print(f"\n{'='*72}")
        print(f"PAGE {pg_num}")
        print('='*72)
        print(text if text else "(no text)")
