import pdfplumber

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    page = pdf.pages[2] # page 3 is index 2
    print(page.extract_text())
