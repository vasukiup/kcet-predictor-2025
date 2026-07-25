import pdfplumber

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    # Page 9 or page 10 of PDF
    page = pdf.pages[8] # index 8 is page 9
    text = page.extract_text()
    print(text[:2500])
