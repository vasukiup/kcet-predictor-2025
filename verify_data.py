"""
Data Verification Script
Compares extracted JSON data against raw PDF text for spot-checking accuracy.
"""
import pdfplumber
import json
import re

PDF_PATH = "Seat_Matrix_05072025.pdf"
JSON_PATH = "seat_matrix_data.json"

# ─────────────────────────────────────────────
# Load extracted JSON
# ─────────────────────────────────────────────
with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

colleges = data["colleges"]

print("=" * 70)
print("EXTRACTION VERIFICATION REPORT")
print("=" * 70)
print(f"\nJSON claims: {data['metadata']['total_colleges']} colleges, {data['metadata']['total_courses_offered']} courses")
print(f"Total seats: {data['stats']['total_seats']:,}")
print(f"Total KEA seats: {data['stats']['total_kea_seats']:,}")

# ─────────────────────────────────────────────
# Spot check extracted data (show first 10 colleges)
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("EXTRACTED DATA - First 10 Colleges")
print("=" * 70)
for col in colleges[:10]:
    ann = col.get("annexure", "?")
    name = col.get("college_name", "?")
    ti = col.get("total_intake", 0)
    tk = col.get("total_kea_seats", 0)
    dist = col.get("district", "?")
    print(f"\n[{ann}] {name} | District: {dist}")
    print(f"     Total Intake: {ti} | Total KEA: {tk}")
    for c in col.get("courses", []):
        row = (
            f"     -> {c['course_name'][:45]:<45} "
            f"| intake={c.get('total_intake',0):>4} "
            f"| kea={c.get('total_kea_seats',0):>4} "
            f"| ph={c.get('kea_ph',0):>2} "
            f"| hk={c.get('kea_hk',0):>2} "
            f"| rk={c.get('kea_rk',0):>3} "
            f"| cat2={c.get('cat2_seats',0):>4} "
            f"| cat3={c.get('cat3_seats',0):>4}"
        )
        print(row)

# ─────────────────────────────────────────────
# Now compare against raw PDF text for those colleges
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("RAW PDF TEXT - Cross-checking pages 3-10 (Annexure A)")
print("=" * 70)
with pdfplumber.open(PDF_PATH) as pdf:
    for pg_idx in range(2, 12):  # pages 3-12
        page = pdf.pages[pg_idx]
        text = page.extract_text()
        if text and ("ANNEXURE" in text or any(c.get("college_name","")[:20].upper() in text.upper() for c in colleges[:10])):
            print(f"\n--- PAGE {pg_idx + 1} ---")
            print(text[:3000])

# ─────────────────────────────────────────────
# Compare a specific college: Annexure A, GEC Arasikere
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("DEEP CHECK: GEC Arasikere (should be 4 courses, 240 total intake)")
print("=" * 70)

target = next((c for c in colleges if "ARASIKERE" in c.get("college_name","").upper()), None)
if target:
    print("EXTRACTED:")
    print(f"  Name: {target['college_name']}")
    print(f"  Total Intake: {target.get('total_intake')} | KEA: {target.get('total_kea_seats')}")
    for c in target["courses"]:
        print(f"  {c['course_name']} | intake={c.get('total_intake')} | kea={c.get('total_kea_seats')} | ph={c.get('kea_ph')} | spl={c.get('kea_spl')} | hk={c.get('kea_hk')} | rk={c.get('kea_rk')} | tot={c.get('kea_tot')}")
else:
    print("  NOT FOUND in extracted data!")

# ─────────────────────────────────────────────
# Check how many colleges have missing course details
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("DATA QUALITY CHECKS")
print("=" * 70)

no_courses = [c for c in colleges if not c.get("courses")]
zero_intake = [c for c in colleges if c.get("total_intake", 0) == 0 and not c.get("courses")]
missing_district = [c for c in colleges if not c.get("district") or c.get("district") == "Other"]

print(f"Colleges with NO courses extracted: {len(no_courses)}")
for c in no_courses[:5]:
    print(f"  [{c['annexure']}] {c['college_name']}")

print(f"\nColleges with 0 total_intake (and no courses): {len(zero_intake)}")
print(f"Colleges with unknown district: {len(missing_district)}")
for c in missing_district[:10]:
    print(f"  [{c['annexure']}] {c['college_name']} | address: {c.get('address','')[:60]}")

# ─────────────────────────────────────────────
# Cross-check: Do sub-totals add up?
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("INTERNAL CONSISTENCY CHECK")
print("=" * 70)
mismatches = 0
for col in colleges:
    claimed_intake = col.get("total_intake", 0)
    summed_intake = sum(c.get("total_intake", 0) for c in col.get("courses", []))
    claimed_kea = col.get("total_kea_seats", 0)
    summed_kea = sum(c.get("total_kea_seats", 0) for c in col.get("courses", []))
    
    if claimed_intake > 0 and abs(claimed_intake - summed_intake) > 5:
        print(f"MISMATCH [{col['annexure']}] {col['college_name'][:50]}")
        print(f"  total_intake claimed={claimed_intake}, sum of courses={summed_intake}")
        mismatches += 1
    if claimed_kea > 0 and abs(claimed_kea - summed_kea) > 5:
        print(f"MISMATCH [{col['annexure']}] {col['college_name'][:50]}")
        print(f"  total_kea claimed={claimed_kea}, sum of courses={summed_kea}")
        mismatches += 1

if mismatches == 0:
    print("All colleges: total_intake and total_kea_seats match sum of their courses. OK")
else:
    print(f"\nTotal mismatches found: {mismatches}")

print("\nDONE.")
