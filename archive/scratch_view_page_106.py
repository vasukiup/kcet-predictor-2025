import pdfplumber

def view_page_106():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[105] # page 106 (Index 105)
        print("=== Page 106 Text ===")
        print(page.extract_text())

if __name__ == "__main__":
    view_page_106()
