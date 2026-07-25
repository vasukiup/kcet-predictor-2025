"""
Before/After comparison report:
  - v1 baseline vs v2 improved extractor
  - vs PDF ground truth (from serial number scan)
"""
import json

PDF_GROUND_TRUTH = {
    "A": {"label": "Government / VTU Constituent",  "colleges": 22,  "note": "All serial numbers 1-22 found"},
    "B": {"label": "Government Aided",               "colleges": 8,   "note": "Serials 1-8 (serial 7 on image page)"},
    "C": {"label": "Private Unaided",                "colleges": 146, "note": "Serials 1-146 confirmed"},
    "D": {"label": "Private Minority",               "colleges": 25,  "note": "Serials 1-25 confirmed"},
}

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    v1 = json.load(f)

with open("seat_matrix_data.json", encoding="utf-8") as f:
    v2 = json.load(f)

def ann_stats(data, ann):
    cols = [c for c in data["colleges"] if c["annexure"] == ann]
    seats = sum(c.get("total_intake", 0) for c in cols)
    kea   = sum(c.get("total_kea_seats", 0) for c in cols)
    courses_per_col = [len(c.get("courses", [])) for c in cols]
    zero_courses = sum(1 for x in courses_per_col if x == 0)
    avg_courses = sum(courses_per_col) / len(courses_per_col) if courses_per_col else 0
    return {
        "colleges": len(cols),
        "seats": seats,
        "kea": kea,
        "zero_courses": zero_courses,
        "avg_courses": round(avg_courses, 1),
    }

SEP = "=" * 72

print(SEP)
print("  BEFORE vs AFTER COMPARISON REPORT")
print("  v1 Baseline  vs  v2 Multi-page Stitching  vs  PDF Ground Truth")
print(SEP)

for ann in ["A", "B", "C", "D"]:
    gt  = PDF_GROUND_TRUTH[ann]
    s1  = ann_stats(v1, ann)
    s2  = ann_stats(v2, ann)

    def mark(val, expected, field="colleges"):
        if field == "colleges":
            if val == expected: return "✅"
            elif abs(val - expected) <= 2: return "~"
            else: return "❌"
        return ""

    print(f"\n  Annexure {ann} — {gt['label']}")
    print(f"  PDF Ground Truth: {gt['colleges']} colleges  ({gt['note']})")
    print(f"  {'':30s}  {'v1':>8}  {'v2':>8}  {'PDF':>8}")
    print(f"  {'Colleges':30s}  {s1['colleges']:>8}  {s2['colleges']:>8}  {gt['colleges']:>8}  "
          f"v1={mark(s1['colleges'], gt['colleges'])}  v2={mark(s2['colleges'], gt['colleges'])}")
    print(f"  {'Total Seats':30s}  {s1['seats']:>8,}  {s2['seats']:>8,}")
    print(f"  {'Total KEA Seats':30s}  {s1['kea']:>8,}  {s2['kea']:>8,}")
    print(f"  {'Colleges w/ 0 courses':30s}  {s1['zero_courses']:>8}  {s2['zero_courses']:>8}")
    print(f"  {'Avg courses per college':30s}  {s1['avg_courses']:>8}  {s2['avg_courses']:>8}")

print(f"\n{SEP}")
print("  OVERALL TOTALS")
print(SEP)

def totals(data):
    cols = data["colleges"]
    return {
        "colleges": len(cols),
        "seats": sum(c.get("total_intake", 0) for c in cols),
        "kea": sum(c.get("total_kea_seats", 0) for c in cols),
        "courses": data["metadata"]["total_courses_offered"],
    }

t1 = totals(v1)
t2 = totals(v2)
pdf_total = sum(v["colleges"] for v in PDF_GROUND_TRUTH.values())

print(f"  {'':30s}  {'v1':>8}  {'v2':>8}  {'PDF':>8}")
print(f"  {'Total Colleges':30s}  {t1['colleges']:>8}  {t2['colleges']:>8}  {pdf_total:>8}")
print(f"  {'Total Seats':30s}  {t1['seats']:>8,}  {t2['seats']:>8,}")
print(f"  {'Total KEA Seats':30s}  {t1['kea']:>8,}  {t2['kea']:>8,}")
print(f"  {'Unique Courses':30s}  {t1['courses']:>8}  {t2['courses']:>8}")

print(f"\n{SEP}")
print("  COLLEGE COUNT ACCURACY vs PDF GROUND TRUTH")
print(SEP)
total_pdf = 0
total_v1  = 0
total_v2  = 0
for ann in ["A", "B", "C", "D"]:
    gt = PDF_GROUND_TRUTH[ann]["colleges"]
    s1 = ann_stats(v1, ann)["colleges"]
    s2 = ann_stats(v2, ann)["colleges"]
    diff1 = s1 - gt
    diff2 = s2 - gt
    status1 = "exact" if diff1 == 0 else f"{diff1:+d}"
    status2 = "exact" if diff2 == 0 else f"{diff2:+d}"
    print(f"  [{ann}] PDF={gt:3d}  v1={s1:3d} ({status1:>6})  v2={s2:3d} ({status2:>6})")
    total_pdf += gt
    total_v1  += s1
    total_v2  += s2

diff1t = total_v1 - total_pdf
diff2t = total_v2 - total_pdf
print(f"  [TOTAL] PDF={total_pdf}  v1={total_v1} ({diff1t:+d})  v2={total_v2} ({diff2t:+d})")

print(f"\n{SEP}")
print("  INTERNAL CONSISTENCY (sum of courses == college totals)")
print(SEP)
for label, data in [("v1", v1), ("v2", v2)]:
    mismatches = 0
    for col in data["colleges"]:
        ti = col.get("total_intake", 0)
        tk = col.get("total_kea_seats", 0)
        si = sum(c.get("total_intake", 0) for c in col.get("courses", []))
        sk = sum(c.get("total_kea_seats", 0) for c in col.get("courses", []))
        if ti > 0 and abs(ti - si) > 5:
            mismatches += 1
    print(f"  {label}: colleges with intake mismatch = {mismatches}")

print(f"\n{SEP}")
print("  WHAT'S STILL MISSING (v2)")
print(SEP)
missing_in_v2 = []
for ann in ["A", "B", "C", "D"]:
    gt = PDF_GROUND_TRUTH[ann]["colleges"]
    s2 = ann_stats(v2, ann)["colleges"]
    if s2 < gt:
        missing_in_v2.append(f"  Annexure {ann}: expected {gt}, got {s2} (missing {gt - s2})")
if missing_in_v2:
    for m in missing_in_v2:
        print(m)
else:
    print("  None — all colleges accounted for")
