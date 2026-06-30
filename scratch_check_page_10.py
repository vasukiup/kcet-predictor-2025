import pdfplumber

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    # Page 10 is index 9
    for pg_idx in [9, 10]:
        page = pdf.pages[pg_idx]
        text = page.extract_text()
        print(f"\n================ PAGE {pg_idx + 1} ================")
        print(text[:2500])
