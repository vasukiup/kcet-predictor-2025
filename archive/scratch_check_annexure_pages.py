import pypdf
import re

reader = pypdf.PdfReader("Seat_Matrix_05072025.pdf")
for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    if "ANNEXURE :" in text:
        matches = re.findall(r'ANNEXURE\s*:\s*([A-Z])', text)
        print(f"Page {idx+1}: contains matches {matches}")
