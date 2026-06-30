import pdfplumber

def view_page_418():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[417] # page 418 (Index 417)
        print("=== Page 418 Text ===")
        print(page.extract_text())

if __name__ == "__main__":
    view_page_418()
