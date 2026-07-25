"""
Wait, why did find_missing_headers report that college #47 is missing from the headers?
Let's check the college number sequence in Annexure E.
Is there actually a college #47, or does the numbering skip some values?
Let's print all college header numbers found, and the lines where they occur.
Let's print the actual list of headers found between 40 and 60.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

print("=== College Headers Found (40-60) ===")
for pg in range(122, 324):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        m = re.match(r'^(\d{1,3})\s+([A-Z].*)$', line.strip())
        if m:
            num = int(m.group(1))
            if 40 <= num <= 60:
                print(f"Page {pg}: {num} - {m.group(2)[:60]}")
