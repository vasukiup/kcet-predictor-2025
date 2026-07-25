import pdfplumber

def view_page_362():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[361] # 0-indexed page 362
        text = page.extract_text()
        print("=== Page 362 Text ===")
        print(text)

if __name__ == "__main__":
    view_page_362()
