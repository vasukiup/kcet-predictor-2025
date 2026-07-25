import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

try:
    reader = pypdf.PdfReader("Seat_Matrix_05072025.pdf")
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if "Sri Venkateshwara College of Engineering" in text or "Sri Venkateswara College of Engineering" in text:
            print(f"PyPDF Found on 1-based page: {idx + 1}")
            print(text[:2000])
            print("-" * 50)
except Exception as e:
    print("Error:", e)
