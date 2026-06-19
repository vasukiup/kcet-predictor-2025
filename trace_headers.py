"""
Let's trace if there is another college header or if we are double counting due to duplicate pages or something.
Wait, let's print all college headers printed between page 130 and 150.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for pg in range(130, 151):
    text = pdf.pages[pg-1].extract_text() or ""
    print(f"\n--- Page {pg} ---")
    for line in text.splitlines():
        m = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$', line.strip())
        if m:
            print(f"Header: {m.group(0)}")
        if "TOT " in line:
            print(f"Total line: {line.strip()}")
