import pdfplumber

def check_lengths():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        num_pages = len(pdf.pages)
        print(f"Total pages: {num_pages}")
        for pg in range(359, num_pages):
            text = pdf.pages[pg].extract_text() or ""
            print(f"Page {pg+1}: text length = {len(text)}")
            if len(text) > 0:
                print(f"  First line: {text.splitlines()[0] if text.splitlines() else 'None'}")

if __name__ == "__main__":
    check_lengths()
