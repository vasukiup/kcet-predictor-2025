"""
Extract and print the full course rows and TOT rows for page 122 and 123
to analyze why PH is 40 (course sum) vs 33 (TOT sum), and SPL is 11 vs 7.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for pg in [122, 123]:
    print(f"\n=== PAGE {pg} ===")
    text = pdf.pages[pg-1].extract_text() or ""
    for line in text.splitlines():
        # print RK, HK, and TOT lines
        if line.strip().startswith("RK ") or line.strip().startswith("HK ") or line.strip().startswith("TOT ") or "KM QUOTA" in line:
            print(line.strip())
