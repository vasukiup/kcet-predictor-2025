"""
Find which Annexure D colleges have wrong intake totals.
Compare our course sums against the Ins Total lines extracted from PDF pages 94-101.
"""
import pdfplumber, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")

# PDF Ins Total per college (extracted from pages 94-101):
PDF_INS_TOTALS = {
    1: 780,   # A J Institute
    2: 510,   # Anjuman
    3: 300,   # Bahubali
    4: 330,   # Beary's
    5: 750,   # Canara
    6: 480,   # Ghousia
    7: 780,   # Gurunanak Dev
    8: 840,   # HKBK
    9: 270,   # KCT
    10: 1170, # MVJ
    11: 1020, # New Horizon
    12: 390,  # PA College
    13: 420,  # SDM Ujire
    14: 660,  # SDM Dharwad
    15: 840,  # St Joseph
    16: 900,  # Oxford
}

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

ann_d = sorted([c for c in d["colleges"] if c["annexure"] == "D"], key=lambda x: x["college_number"])

print(f"{'#':>3} {'College':<50} {'PDF':>6} {'Ours':>6} {'Diff':>6}")
print("-"*75)
total_diff = 0
for col in ann_d:
    num = col["college_number"]
    pdf_total = PDF_INS_TOTALS.get(num, 0)
    our_total = sum(c["total_intake"] for c in col["courses"])
    diff = our_total - pdf_total
    total_diff += diff
    flag = "  <--- MISMATCH" if diff != 0 else ""
    print(f"{num:>3} {col['college_name'][:50]:<50} {pdf_total:>6} {our_total:>6} {diff:>+6}{flag}")

print("-"*75)
print(f"{'Total diff':>60} {total_diff:>+6}")
print(f"\nPDF Grand Total: 10440, Our Total: {sum(c['total_intake'] for col in ann_d for c in col['courses'])}")
print(f"Need {10440 - sum(c['total_intake'] for col in ann_d for c in col['courses'])} more seats")
