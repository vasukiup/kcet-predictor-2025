"""
Full Annexure D audit:
1. Check current DB state
2. Scan PDF for page ranges, image pages, college numbers
3. Render image pages
4. Find grand total row
"""
import json, pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

ann_d = sorted([c for c in d["colleges"] if c["annexure"] == "D"], key=lambda x: x["college_number"])
print(f"Annexure D currently in DB: {len(ann_d)}/16 colleges")
for c in ann_d:
    ti = sum(cr["total_intake"] for cr in c["courses"])
    print(f"  #{c['college_number']:>2} {c['college_name'][:58]:<58} | courses={len(c['courses']):>2} | intake={ti:>5}")

print()
print("Scanning PDF for Annexure D pages...")

college_pages = {}
image_pages = []
total_lines = []
in_d = False

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in range(1, len(pdf.pages) + 1):
        page = pdf.pages[pg_num - 1]
        text = page.extract_text() or ""
        chars = len(page.chars)
        imgs  = len(page.images)

        if "ANNEXURE : D" in text:
            in_d = True

        if in_d and pg_num > 94 and ("ANNEXURE : E" in text or "ANNEXURE : M" in text or "ANNEXURE : O" in text):
            print(f"  Annexure D ends before page {pg_num}")
            break

        if in_d:
            if chars == 0 and imgs > 0:
                image_pages.append(pg_num)
                print(f"  IMAGE-ONLY page {pg_num}")
                page.to_image(resolution=140).save(f"annD_page{pg_num}.png")
                print(f"    -> saved annD_page{pg_num}.png")
            else:
                # College headers
                for m in re.finditer(r'^(\d+)\s+[A-Z]', text, re.MULTILINE):
                    num = int(m.group(1))
                    if 1 <= num <= 20:
                        if num not in college_pages:
                            college_pages[num] = pg_num

                # Total row
                for line in text.splitlines():
                    if "TOTAL" in line and "Annexure" in line:
                        total_lines.append((pg_num, line.strip()))
                        print(f"  TOTAL ROW on page {pg_num}: {line.strip()}")

pdf_nums = sorted(college_pages.keys())
db_nums  = [c["college_number"] for c in ann_d]
missing  = [n for n in range(1, 17) if n not in db_nums]

print(f"\nCollege numbers found in PDF text: {pdf_nums}")
print(f"College numbers in DB:            {db_nums}")
print(f"Missing from DB:                  {missing}")
print(f"Image-only pages:                 {image_pages}")
print(f"Total row(s) found:               {total_lines}")
