"""
Scan Annexure E (pages 122-323) and V (325-360):
1. Find all college headers (number + name)
2. Find all Ins Total rows
3. Find grand total rows
4. Render key pages as images
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

RANGES = {"E": range(122, 324), "V": range(325, 361)}

for ann, pages in RANGES.items():
    print(f"\n{'='*70}")
    print(f"  ANNEXURE {ann}  (pages {pages.start}-{pages.stop-1})")
    print('='*70)
    colleges = {}      # num -> (name, page)
    ins_totals = {}    # num -> values
    grand_total = None
    image_pages = []
    current_col = None

    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        for pg in pages:
            page = pdf.pages[pg-1]
            text = page.extract_text() or ""
            chars = len(page.chars)
            imgs  = len(page.images)

            if chars == 0 and imgs > 0:
                image_pages.append(pg)
                continue

            lines = text.splitlines()
            for i, line in enumerate(lines):
                stripped = line.strip()

                # Grand total
                if re.search(r'TOTAL\s*[:\-]\s*Annexure\s*[-\s]*' + ann, stripped, re.I):
                    grand_total = stripped
                    print(f"  GRAND TOTAL (pg {pg}): {stripped}")

                # College header — digit(s) then college name
                m = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$', stripped)
                if m:
                    num = int(m.group(1))
                    if 1 <= num <= 500:
                        colleges[num] = (m.group(2).strip(), pg)
                        current_col = num

                # Ins Total
                if "Ins Total" in stripped and current_col:
                    vals = [int(x) for x in re.findall(r'\d+', stripped)]
                    if vals:
                        ins_totals[current_col] = vals[0]  # first number = intake

    nums = sorted(colleges.keys())
    print(f"\n  Colleges found: {len(colleges)}  (#{nums[0] if nums else '?'} to #{nums[-1] if nums else '?'})")
    print(f"  Image pages: {image_pages}")
    print(f"  Grand total line: {grand_total}")
    print(f"\n  College list (first 10):")
    for num in nums[:10]:
        name, pg = colleges[num]
        itake = ins_totals.get(num, "?")
        print(f"    #{num:>3}  pg{pg:>4}  intake={itake:>6}  {name[:55]}")
    if len(nums) > 10:
        print(f"    ... and {len(nums)-10} more ...")
        for num in nums[-5:]:
            name, pg = colleges[num]
            itake = ins_totals.get(num, "?")
            print(f"    #{num:>3}  pg{pg:>4}  intake={itake:>6}  {name[:55]}")

    # Render first 2 text pages and any image pages
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        first_pg = pages.start
        pdf.pages[first_pg-1].to_image(resolution=130).save(f"ann{ann}_first.png")
        print(f"\n  Rendered ann{ann}_first.png (page {first_pg})")
        if image_pages:
            pdf.pages[image_pages[0]-1].to_image(resolution=130).save(f"ann{ann}_img1.png")
            print(f"  Rendered ann{ann}_img1.png (page {image_pages[0]})")
