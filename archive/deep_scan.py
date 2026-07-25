"""
Deep scan to:
1. Find all annexure headers in pages 104-435
2. Find TOTAL rows for O, P, Z
3. Understand P's true structure (is it really 317 pages?)
4. Find where Z is hiding
5. Count colleges in O and render image page 118
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    total_pages = len(pdf.pages)

    print("=== ANNEXURE HEADER SCAN (pages 104-435) ===")
    ann_changes = []
    for pg in range(104, total_pages + 1):
        text = pdf.pages[pg-1].extract_text() or ""
        # Find any ANNEXURE header
        for m in re.finditer(r'ANNEXURE\s*[:\-]\s*([A-Z])\b', text):
            ann = m.group(1)
            ann_changes.append((pg, ann))
            print(f"  pg {pg:>4}: ANNEXURE {ann}")
            break

    print()
    print("=== TOTAL ROWS (pages 104-435) ===")
    for pg in range(104, total_pages + 1):
        text = pdf.pages[pg-1].extract_text() or ""
        for line in text.splitlines():
            if re.search(r'TOTAL\s*:\s*Annexure', line, re.IGNORECASE):
                print(f"  pg {pg:>4}: {line.strip()}")

    print()
    print("=== COLLEGE COUNT IN ANNEXURE O (pages 104-118) ===")
    o_colleges = set()
    for pg in range(104, 119):
        text = pdf.pages[pg-1].extract_text() or ""
        for m in re.finditer(r'^(\d{1,3})\s+[A-Z][A-Z\s]{5,}', text, re.MULTILINE):
            num = int(m.group(1))
            if 1 <= num <= 30:
                o_colleges.add(num)
    print(f"  College numbers found in O: {sorted(o_colleges)}")
    print(f"  Count: {len(o_colleges)}")

    print()
    print("=== RENDERING IMAGE PAGES ===")
    for pg in [118, 120, 121]:
        page = pdf.pages[pg-1]
        page.to_image(resolution=140).save(f"scan_page{pg}.png")
        print(f"  Saved scan_page{pg}.png")
