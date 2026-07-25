"""
Write a quick script to find the total page count of the PDF,
and scan the text of pages in E and V to see if there are any lines starting with "TOTAL" or "Annexure Total" or similar.
"""
import pdfplumber, re
pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")
print("Total pages in PDF:", len(pdf.pages))

# Search for any page containing TOTAL or Annexure Total in E and V pages
ranges = {"E": range(122, 324), "V": range(325, 361)}

for name, pg_range in ranges.items():
    print(f"\n--- Checking Annexure {name} ({pg_range.start} to {pg_range.stop-1}) ---")
    for pg in pg_range:
        text = pdf.pages[pg-1].extract_text() or ""
        for line in text.splitlines():
            if "total" in line.lower() or "tot" in line.lower():
                # print any lines that look like grand totals (not course lines or TOT code)
                # and check if it has large numbers or says Annexure Total
                if "annexure" in line.lower() or "grand" in line.lower() or ("tot" in line.lower() and len(re.findall(r'\d+', line)) > 10):
                    print(f"Page {pg}: {line}")
