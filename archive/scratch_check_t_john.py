import pdfplumber

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    page = pdf.pages[86]  # page 87 is index 86
    text = page.extract_text()
    lines = text.split("\n")
    found = False
    for idx, line in enumerate(lines):
        if "T.John Institute of technology" in line:
            found = True
        if found:
            print(f"{idx}: {line}")
