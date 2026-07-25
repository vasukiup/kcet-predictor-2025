"""
Analyze the details of a single college in Annexure E to see howcourses, quotas, and special categories are structured.
Let's print the entire text of page 122 (constituent college of VTU) to study the row structure.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    print(pdf.pages[121].extract_text())
