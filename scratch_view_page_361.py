import pdfplumber

def view_page_361():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[360] # 0-indexed page 361
        text = page.extract_text()
        print("=== Page 361 Text ===")
        print(text[:2000])

if __name__ == "__main__":
    view_page_361()
