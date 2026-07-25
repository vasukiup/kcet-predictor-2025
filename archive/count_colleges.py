"""
Step 1: Scan the PDF to find the true college counts per annexure
and the page ranges for each annexure.
"""
import pdfplumber
import re

PDF_PATH = "Seat_Matrix_05072025.pdf"

annexure_pages = {}   # annexure -> list of pages that contain it
college_numbers = {}  # annexure -> set of college serial numbers seen
last_annexure = None

print("Scanning PDF for annexure boundaries and college serial numbers...\n")

with pdfplumber.open(PDF_PATH) as pdf:
    total = len(pdf.pages)
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue

        # Detect annexure
        for ann in ["A", "B", "C", "D", "E"]:
            if f"ANNEXURE : {ann}" in text:
                last_annexure = ann
                break

        if last_annexure not in ["A", "B", "C", "D"]:
            continue

        if last_annexure not in annexure_pages:
            annexure_pages[last_annexure] = []
            college_numbers[last_annexure] = set()
        annexure_pages[last_annexure].append(i + 1)  # 1-indexed page number

        # Find college serial numbers - lines like "123 CollegeName"
        # followed by "Address :"
        lines = text.splitlines()
        for j, line in enumerate(lines):
            line = line.strip()
            m = re.match(r'^(\d+)\s+\S', line)
            if m:
                num = int(m.group(1))
                # check if next non-empty line is Address or if it looks like a college header
                # Avoid matching course numbers (they're also numbered)
                for k in range(j+1, min(j+4, len(lines))):
                    nxt = lines[k].strip()
                    if nxt.startswith("Address"):
                        college_numbers[last_annexure].add(num)
                        break
                    elif nxt and not re.match(r'^\d', nxt):
                        # could be continuation of college name
                        continue

print("Annexure page ranges:")
for ann in ["A", "B", "C", "D"]:
    pages = annexure_pages.get(ann, [])
    nums = sorted(college_numbers.get(ann, set()))
    if pages:
        print(f"  Annexure {ann}: pages {pages[0]}–{pages[-1]}  ({len(pages)} pages)")
        print(f"    College serial numbers found: {nums}")
        print(f"    Max serial number: {max(nums) if nums else 'N/A'}")
        print()
