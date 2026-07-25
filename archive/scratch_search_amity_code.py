import pdfplumber

def search():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        for pg_num in range(len(pdf.pages)):
            text = pdf.pages[pg_num - 1].extract_text() or ""
            if "e302" in text.lower() or "devanahalli" in text.lower():
                print(f"Page {pg_num}: contains E302/Devanahalli. First 200 chars:")
                print(text[:200])
                print("-" * 50)

if __name__ == "__main__":
    search()
