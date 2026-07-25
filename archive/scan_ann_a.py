"""
Scan the PDF pages from index 1 to 121 (original A, B, C, D) to find all colleges with annexure 'A'.
Let's see if there is a college #23.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

print("=== Scanning Annexure A in PDF (pages 1 to 20) ===")
# Annexure A is government colleges at the start of the PDF
for pg in range(1, 20):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        stripped = line.strip()
        m = re.match(r'^(\d{1,2})\s+([A-Z].*)$', stripped)
        if m:
            num = int(m.group(1))
            print(f"Page {pg}: #{num} - {m.group(2)[:60]}")
