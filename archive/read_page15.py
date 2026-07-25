"""
Try to extract table data from page 15 (image page with colleges #7 and #8 of Annexure B).
Try pdfplumber's table extraction, then pdfminer word-level extraction.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    page = pdf.pages[14]  # page 15, 0-indexed

    print("=== Method 1: extract_text() ===")
    t = page.extract_text()
    print(t if t else "(none)")

    print("\n=== Method 2: extract_text(x_tolerance=3, y_tolerance=3) ===")
    t2 = page.extract_text(x_tolerance=3, y_tolerance=3)
    print(t2 if t2 else "(none)")

    print("\n=== Method 3: extract_words() ===")
    words = page.extract_words()
    if words:
        for w in words:
            print(f"  [{w['x0']:.0f},{w['top']:.0f}] '{w['text']}'")
    else:
        print("(no words found)")

    print("\n=== Method 4: extract_tables() ===")
    tables = page.extract_tables()
    if tables:
        for i, tbl in enumerate(tables):
            print(f"Table {i+1}:")
            for row in tbl:
                print("  ", row)
    else:
        print("(no tables found)")

    print("\n=== Page metadata ===")
    print(f"  Width: {page.width}, Height: {page.height}")
    print(f"  Images on page: {len(page.images)}")
    print(f"  Chars on page: {len(page.chars)}")
