import pdfplumber

def check_pages():
    pages_to_check = [362, 370, 380, 420]
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        for pg_num in pages_to_check:
            print(f"\n================ Page {pg_num} ================")
            text = pdf.pages[pg_num - 1].extract_text() or ""
            lines = text.splitlines()
            print("\n".join(lines[:15])) # Print the first 15 lines of each page
            print("...")
            print("\n".join(lines[-5:])) # Print the last 5 lines

if __name__ == "__main__":
    check_pages()
