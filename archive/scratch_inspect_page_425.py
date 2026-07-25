import pdfplumber

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    text = pdf.pages[424].extract_text() # page 425 (Index 424)
    print("=== Raw Text of Page 425 ===")
    for idx, line in enumerate(text.splitlines()):
        print(f"Line {idx+1}: '{line}'")
