"""
Print lines matching college number 25, 47, 50, 75, 113, 123, 124, 159, 168, 170 in E pages
to see what their lines look like.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

missing_nums = [25, 47, 50, 75, 113, 123, 124, 159, 168, 170]

for pg in range(122, 324):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        stripped = line.strip()
        # Find any line starting with a missing number followed by text
        for num in missing_nums:
            if re.match(r'^' + str(num) + r'\b', stripped):
                print(f"Page {pg}: {stripped}")
