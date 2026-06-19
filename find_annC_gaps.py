"""
Find the missing 147th college in Annexure C.
Also find image-only pages in the Annexure C range (pages 16-93).
Then check the grand total row to understand what we need.
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    total_pages = len(pdf.pages)

    # Scan Annexure C pages for image-only pages and find the total row
    in_c = False
    image_pages = []
    total_row_page = None
    total_row_text = None

    for pg_num in range(1, total_pages + 1):
        page = pdf.pages[pg_num - 1]
        text = page.extract_text() or ""
        chars = len(page.chars)
        imgs  = len(page.images)

        if "ANNEXURE : C" in text:
            in_c = True

        if in_c and ("ANNEXURE : D" in text or "ANNEXURE : E" in text):
            print(f"Annexure C ends at page {pg_num}")
            break

        if in_c:
            if chars == 0 and imgs > 0:
                image_pages.append(pg_num)
                print(f"  IMAGE-ONLY page {pg_num} (images={imgs})")

            # Look for grand total row
            if "TOTAL" in text and "Annexure" in text and "C" in text:
                for line in text.splitlines():
                    if "TOTAL" in line and ("Annexure" in line or "C" in line):
                        total_row_text = line.strip()
                        total_row_page = pg_num
                        print(f"  TOTAL ROW found on page {pg_num}: {line.strip()}")

    print(f"\nImage-only pages in Annexure C: {image_pages}")

    # Render each image page to check what's there
    for pg in image_pages:
        page = pdf.pages[pg - 1]
        img = page.to_image(resolution=130)
        fname = f"annC_page{pg}.png"
        img.save(fname)
        print(f"  Saved {fname}")
