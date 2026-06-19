"""
Let's check Annexure V sequence.
List all numbers in range 1 to 30.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

all_nums = set()
for pg in range(325, 361):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        m = re.match(r'^(\d{1,2})\s+([A-Z].*)$', line.strip())
        if m:
            all_nums.add(int(m.group(1)))

print("Total numbers found in V:", len(all_nums))
print("Gaps in V:", sorted(list(set(range(1, 31)) - all_nums)))
