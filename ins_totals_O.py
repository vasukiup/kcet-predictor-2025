"""Print only Ins Total lines and college number headers from Annexure O pages."""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg in range(104, 118):
        text = pdf.pages[pg-1].extract_text() or ""
        lines = text.splitlines()
        print(f"=== PAGE {pg} ===")
        for line in lines:
            stripped = line.strip()
            # College header line: starts with 1-2 digits then uppercase text
            if re.match(r'^\d{1,2}\s+[A-Z][A-Za-z\s\(\)&\.\,\'\-]{5,}$', stripped):
                m = re.match(r'^(\d{1,2})\s+', stripped)
                if m and 1 <= int(m.group(1)) <= 30:
                    print(f"  COL: {stripped[:70]}")
            # Ins Total line
            if "Ins Total" in line:
                print(f"  INS: {stripped}")
        print()
