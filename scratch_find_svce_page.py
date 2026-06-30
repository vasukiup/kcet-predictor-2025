import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        if "Sri Venkateshwara College of Engineering" in text or "Sri Venkateswara College of Engineering" in text:
            print(f"Found on 1-based page: {idx + 1}")
            print(text[:1000]) # Print first 1000 characters
            print("-" * 50)
