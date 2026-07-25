"""
Wait, why did find_missing_headers report that college #47, #50, #75, #113, #123, #124, #159, #168 are missing?
Let's check our check_missing_pages script output:
- Page 172: it starts with RK rows, there is no college header on page 172. Where is the header for college #47?
Maybe it's on page 171?
Let's search for college #47, #50, #75, #113, #123, #124, #159, #168, #170 header text in the entire PDF range of E (122-323).
We will print any line containing "47 ", "50 ", "75 ", etc. at the beginning of a line.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

missing_nums = [47, 50, 75, 113, 123, 124, 159, 168, 170]

for pg in range(122, 324):
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        stripped = line.strip()
        # Regex to match a digit (like 47) at the start of a line
        for num in missing_nums:
            if re.match(r'^' + str(num) + r'\b', stripped):
                print(f"Page {pg}: {stripped}")
