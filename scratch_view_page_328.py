import pdfplumber

def view_page_328():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[327] # page 328 (Index 327)
        print("=== Page 328 Text ===")
        print(page.extract_text())

if __name__ == "__main__":
    view_page_328()
