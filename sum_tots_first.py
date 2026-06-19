"""
Calculate the exact sum of TOT rows at the bottom of pages 122 and 123 (Annexure E),
and 325 and 326 (Annexure V), to verify if they match our course-by-course parsed totals.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for name, pages in [("E (122-123)", [122, 123]), ("V (325-326)", [325, 326])]:
    intake = 0
    kea = 0
    ph = 0
    spl = 0
    for pg in pages:
        text = pdf.pages[pg-1].extract_text() or ""
        for line in text.splitlines():
            if line.strip().startswith("TOT "):
                parts = [int(x) for x in re.findall(r'\d+', line)]
                if parts:
                    intake += parts[0]
                    kea += parts[1]
                    ph += parts[2]
                    spl += parts[3]
    print(f"Page-level TOT sum for {name}:")
    print(f"  Intake: {intake}")
    print(f"  KEA:    {kea}")
    print(f"  PH:     {ph}")
    print(f"  SPL:    {spl}")
