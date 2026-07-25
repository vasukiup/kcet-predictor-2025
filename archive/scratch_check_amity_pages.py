import pdfplumber

def search():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        # Check Annexure O page ranges (typically pages 104-121)
        for pg_num in range(104, 122):
            text = pdf.pages[pg_num - 1].extract_text() or ""
            if "amity" in text.lower():
                print(f"Annexure O Page {pg_num}: contains 'Amity'")
                for line in text.splitlines():
                    if "amity" in line.lower() or "total" in line.lower() or "intake" in line.lower() or "kea" in line.lower():
                        print(f"  {line}")
        # Check Annexure V page ranges (typically pages 325-361)
        for pg_num in range(325, 362):
            text = pdf.pages[pg_num - 1].extract_text() or ""
            if "amity" in text.lower():
                print(f"Annexure V Page {pg_num}: contains 'Amity'")
                for line in text.splitlines():
                    if "amity" in line.lower() or "total" in line.lower() or "intake" in line.lower() or "kea" in line.lower():
                        print(f"  {line}")

if __name__ == "__main__":
    search()
