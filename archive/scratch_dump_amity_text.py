import pdfplumber

def dump():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        for pg in [106, 328, 418]:
            print(f"\n================================ PAGE {pg} ================================")
            text = pdf.pages[pg - 1].extract_text() or ""
            print(text)

if __name__ == "__main__":
    dump()
