"""
Scan PDF for ALL annexure letters and their page ranges + college names.
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = "Seat_Matrix_05072025.pdf"

annexure_pages = {}
annexure_colleges = {}  # annexure -> list of (serial, name, page)
current_ann = None

with pdfplumber.open(PDF_PATH) as pdf:
    total = len(pdf.pages)
    print(f"Total pages: {total}\n")

    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue

        # Detect ANY annexure letter
        m = re.search(r'ANNEXURE\s*:\s*([A-Z]+)', text)
        if m:
            ann = m.group(1)
            if ann != current_ann:
                current_ann = ann
                if ann not in annexure_pages:
                    annexure_pages[ann] = []
                    annexure_colleges[ann] = []

        if current_ann and current_ann not in annexure_pages:
            annexure_pages[current_ann] = []

        if current_ann:
            if current_ann not in annexure_pages:
                annexure_pages[current_ann] = []
            annexure_pages[current_ann].append(i + 1)

            # Find college headers
            lines = text.splitlines()
            for j, line in enumerate(lines):
                line = line.strip()
                m2 = re.match(r'^(\d+)\s+(.+)$', line)
                if m2:
                    num = int(m2.group(1))
                    name_candidate = m2.group(2).strip()
                    # Must be followed by Address within 4 lines
                    for k in range(j+1, min(j+5, len(lines))):
                        nxt = lines[k].strip()
                        if nxt.startswith("Address"):
                            annexure_colleges[current_ann].append((num, name_candidate[:70], i+1))
                            break
                        elif nxt and not re.match(r'^(Sl|Course|Intake|SNQ|KEA|CAT)', nxt, re.IGNORECASE):
                            name_candidate += " " + nxt

print("=" * 70)
print("ALL ANNEXURES FOUND IN PDF")
print("=" * 70)

# User-provided ground truth
USER_TRUTH = {
    "A": 23, "B": 8, "C": 147, "D": 16,
    "M": 1, "O": 27, "P": 2, "Z": 1
}

for ann in sorted(annexure_pages.keys()):
    pages = annexure_pages[ann]
    colleges = annexure_colleges.get(ann, [])
    # Dedupe by name (keep first occurrence per name)
    seen_names = set()
    unique_colleges = []
    for num, name, pg in colleges:
        if name not in seen_names:
            seen_names.add(name)
            unique_colleges.append((num, name, pg))

    expected = USER_TRUTH.get(ann, "?")
    status = ""
    if isinstance(expected, int):
        diff = len(unique_colleges) - expected
        if diff == 0: status = "EXACT"
        elif diff > 0: status = f"OVER +{diff}"
        else: status = f"UNDER {diff}"

    if pages:
        print(f"\nAnnexure {ann}: pages {pages[0]}-{pages[-1]} ({len(pages)} pages)")
    else:
        print(f"\nAnnexure {ann}: (no pages found)")
    print(f"  Colleges found: {len(unique_colleges)}  |  Expected: {expected}  |  {status}")
    for num, name, pg in unique_colleges:
        print(f"    p{pg:>3} #{num:>3} {name}")
