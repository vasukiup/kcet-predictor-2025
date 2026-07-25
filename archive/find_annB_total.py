import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

# Check pages 15-16 for the Annexure B grand total row
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in [15, 16]:
        page = pdf.pages[pg_num - 1]
        text = page.extract_text()
        print(f"\n{'='*70}")
        print(f"PAGE {pg_num}")
        print('='*70)
        if text:
            # Only show first 60 lines to find the total row
            lines = text.splitlines()
            for line in lines[:60]:
                if any(kw in line.upper() for kw in ["TOTAL", "ANNEX", "7 ", "8 "]):
                    print(f"  >>> {line}")
                else:
                    print(f"      {line}")
        else:
            print("(no text layer)")
