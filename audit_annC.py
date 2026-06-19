"""
Audit current Annexure C data and scan all Annexure C pages in the PDF.
"""
import json, pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

ann_c = sorted([c for c in d["colleges"] if c["annexure"] == "C"], key=lambda x: x["college_number"])
print(f"Annexure C currently in DB: {len(ann_c)}/147 colleges")
print()

# Find page range for Annexure C in the PDF
print("Scanning PDF for Annexure C colleges...")
college_pages = {}  # college_number -> page

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    total_pages = len(pdf.pages)
    in_annex_c = False
    for pg_num in range(1, total_pages + 1):
        page = pdf.pages[pg_num - 1]
        text = page.extract_text() or ""
        if "ANNEXURE : C" in text:
            in_annex_c = True
        if in_annex_c and ("ANNEXURE : D" in text or "ANNEXURE : E" in text):
            print(f"  Annexure C ends at page {pg_num}")
            break
        if in_annex_c:
            # Find college numbers on this page
            for m in re.finditer(r'^(\d+)\s+[A-Z]', text, re.MULTILINE):
                num = int(m.group(1))
                if 1 <= num <= 200:
                    if num not in college_pages:
                        college_pages[num] = pg_num

# What do we have vs what's in PDF
pdf_nums = sorted(college_pages.keys())
db_nums  = [c["college_number"] for c in ann_c]
missing_nums = [n for n in pdf_nums if n not in db_nums]

print(f"\nCollege numbers found in PDF: {len(pdf_nums)} (#{min(pdf_nums)} to #{max(pdf_nums)})")
print(f"College numbers in DB:       {len(db_nums)}")
print(f"Missing from DB:             {missing_nums}")
print()

# Show colleges in DB with their course counts and intake totals
print("DB Summary (first 10 and last 5):")
for c in ann_c[:10]:
    ti = sum(cr["total_intake"] for cr in c["courses"])
    print(f"  #{c['college_number']:>3} {c['college_name'][:55]:<55} | courses={len(c['courses']):>2} | intake={ti:>5}")
print("  ...")
for c in ann_c[-5:]:
    ti = sum(cr["total_intake"] for cr in c["courses"])
    print(f"  #{c['college_number']:>3} {c['college_name'][:55]:<55} | courses={len(c['courses']):>2} | intake={ti:>5}")
