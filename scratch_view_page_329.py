import pdfplumber

def view_page_329():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[328] # page 329 (Index 328)
        print("=== Page 329 Text ===")
        print(page.extract_text())

if __name__ == "__main__":
    view_page_329()
