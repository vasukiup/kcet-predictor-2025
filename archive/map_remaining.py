"""
Map all remaining annexures in the PDF (O, P, Z and any others).
Find page ranges, image-only pages, grand total rows for each.
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

TARGET_ANNS = {"O", "P", "Z"}
current_ann = None
ann_pages   = {}   # ann -> list of pages
ann_totals  = {}   # ann -> total line text
image_pages = {}   # ann -> list of image pages

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    total = len(pdf.pages)
    print(f"Total pages in PDF: {total}")
    print()

    for pg_num in range(104, total + 1):
        page  = pdf.pages[pg_num - 1]
        text  = page.extract_text() or ""
        chars = len(page.chars)
        imgs  = len(page.images)

        # Detect annexure start
        for ann in TARGET_ANNS:
            if f"ANNEXURE : {ann}" in text or f"ANNEXURE: {ann}" in text:
                current_ann = ann
                if ann not in ann_pages:
                    ann_pages[ann] = []
                    image_pages[ann] = []
                    print(f"  Annexure {ann} starts at page {pg_num}")
                break

        if current_ann not in TARGET_ANNS:
            continue

        if current_ann not in ann_pages:
            ann_pages[current_ann] = []
            image_pages[current_ann] = []

        ann_pages[current_ann].append(pg_num)

        if chars == 0 and imgs > 0:
            image_pages[current_ann].append(pg_num)
            print(f"    IMAGE-ONLY page {pg_num} (ann={current_ann}, images={imgs})")

        # Grand total rows
        for line in text.splitlines():
            if "TOTAL" in line and f"Annexure" in line and f"- {current_ann}" in line:
                ann_totals[current_ann] = line.strip()
                print(f"    TOTAL ROW (ann={current_ann}, pg={pg_num}): {line.strip()}")

print()
print("Summary:")
for ann in TARGET_ANNS:
    pages = ann_pages.get(ann, [])
    imgs  = image_pages.get(ann, [])
    tot   = ann_totals.get(ann, "NOT FOUND")
    print(f"  Annexure {ann}: pages {pages[0] if pages else '?'}-{pages[-1] if pages else '?'} "
          f"({len(pages)} pages, {len(imgs)} image pages)")
    print(f"    Total row: {tot}")
    print(f"    Image pages: {imgs}")
