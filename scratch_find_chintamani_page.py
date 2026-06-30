import pypdf

reader = pypdf.PdfReader("Seat_Matrix_05072025.pdf")
for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    if "Chintamani" in text or "CHINTAMANI" in text:
        print(f"Page {idx+1}: contains 'Chintamani'")
