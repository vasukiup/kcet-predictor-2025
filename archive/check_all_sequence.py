"""
Find the exact list of missing numbers between 1 and 194.
Let's see if the sequence skips these numbers in the PDF document itself.
We will list all numbers present in the document.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

all_nums = set()
for pg in range(122, 324):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        m = re.match(r'^(\d{1,3})\s+([A-Z].*)$', line.strip())
        if m:
            all_nums.add(int(m.group(1)))

print("Total numbers found in E:", len(all_nums))
print("Min number:", min(all_nums))
print("Max number:", max(all_nums))
print("Gaps in E:", sorted(list(set(range(1, 195)) - all_nums)))
