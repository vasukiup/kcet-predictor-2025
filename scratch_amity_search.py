import pdfplumber

def search_amity():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        for pg_num in range(len(pdf.pages)):
            text = pdf.pages[pg_num].extract_text() or ""
            if "amity" in text.lower():
                print(f"Page {pg_num + 1} contains 'Amity'. First 200 chars:")
                print(text[:200])
                print("-" * 50)

if __name__ == "__main__":
    search_amity()
