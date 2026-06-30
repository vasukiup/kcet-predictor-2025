import pdfplumber

def check():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        for pg_num in range(429, 436):
            print(f"\n================================ PAGE {pg_num} ================================")
            text = pdf.pages[pg_num - 1].extract_text() or ""
            print(text)

if __name__ == "__main__":
    check()
