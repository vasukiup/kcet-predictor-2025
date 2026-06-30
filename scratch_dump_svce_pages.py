import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for page_idx in [85, 86, 87]:  # 0-indexed, so page 86, 87, 88
        page = pdf.pages[page_idx]
        text = page.extract_text()
        print(f"\n=================== PAGE {page_idx + 1} ===================")
        print(text)
