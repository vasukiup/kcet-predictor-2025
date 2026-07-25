import pdfplumber

def view_page_330():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[329] # page 330 (Index 329)
        print("=== Page 330 Text ===")
        print(page.extract_text()[:1500]) # Print first 1500 chars

if __name__ == "__main__":
    view_page_330()
