"""
Read page 324 (index 323) which is empty or has headers, and page 325 (index 324) to see if there is any grand total page for E.
Also read page 361 (index 360) to see if there is any grand total page for V.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    print("=== Page 324 ===")
    print(pdf.pages[323].extract_text())
    
    print("\n=== Page 361 ===")
    if len(pdf.pages) > 360:
        print(pdf.pages[360].extract_text()[:2000])
    else:
        print("PDF has only 360 pages.")
