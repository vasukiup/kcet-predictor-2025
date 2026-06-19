"""
Check the last few pages of E (around 320 to 324) and V (around 355 to 360)
to locate the grand total page or see if there is a summary/grand total row at the very end of E or V.
"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    print("=== Pages 321-324 (End of E, Start of V) ===")
    for pg in range(321, 326):
        print(f"\n--- Page {pg} (Index {pg-1}) ---")
        text = pdf.pages[pg-1].extract_text() or ""
        # print first 10 and last 10 lines
        lines = text.splitlines()
        if len(lines) <= 20:
            print(text)
        else:
            print("\n".join(lines[:10]))
            print("...")
            print("\n".join(lines[-10:]))

    print("\n=== Pages 358-361 (End of V) ===")
    for pg in range(358, 361):
        print(f"\n--- Page {pg} (Index {pg-1}) ---")
        text = pdf.pages[pg-1].extract_text() or ""
        lines = text.splitlines()
        if len(lines) <= 20:
            print(text)
        else:
            print("\n".join(lines[:10]))
            print("...")
            print("\n".join(lines[-10:]))
