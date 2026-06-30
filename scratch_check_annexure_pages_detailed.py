import pdfplumber
from extract_seats_v2 import detect_annexure_on_page

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    current_ann = None
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        ann = detect_annexure_on_page(text)
        if ann:
            current_ann = ann
        print(f"Page {idx+1}: detected={ann}, current={current_ann}")
