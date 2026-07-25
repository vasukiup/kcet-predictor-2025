"""
Let's see if we can find pages where:
- A college starts but does not have a college header, or we fail to find its start.
Wait, let's list all college numbers that are printed in Annexure E to see if we missed any numbers or if there are gaps.
The numbers should be 1 to 194.
Let's write a script to find all occurrences of college headers and print any missing numbers.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

print("=== Scanning College Headers in Annexure E ===")
header_nums = set()
for pg in range(122, 324):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        # A header usually starts with a number, then a name.
        m = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$', line.strip())
        if m:
            num = int(m.group(1))
            header_nums.add(num)

missing = sorted(list(set(range(1, 195)) - header_nums))
print("Missing college header numbers in E:", missing)
