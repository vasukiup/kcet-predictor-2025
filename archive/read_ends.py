"""
Check target grand totals or college counts for Annexure E and V from the PDF.
We will search the text of all pages in E (122-323) and V (325-360) for any total-like text,
or let's write a script to compute the sum of 'TOT' rows or 'Ins Total' or similar to see what the PDF shows.
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# Let's search for "Total" or similar at the end of each annexure
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    # Page 323 is the last page of Annexure E (122-323 is 1-based index 122 to 323)
    # Let's print the last page text of E (page 323, 0-indexed 322)
    print("=== Annexure E End (Page 323) ===")
    print(pdf.pages[322].extract_text())
    
    # Page 360 is the last page of Annexure V (325-360 is 1-based index 325 to 360)
    # Let's print the last page text of V (page 360, 0-indexed 359)
    print("\n=== Annexure V End (Page 360) ===")
    print(pdf.pages[359].extract_text())
