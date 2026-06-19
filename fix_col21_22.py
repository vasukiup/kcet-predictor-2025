"""
Fix college #21 (VTU VIAT Muddenahalli) - add missing course + correct all values from PDF text.
Also correct college #22 (VTU CPGS Kalburgi) course values which look different from what we stored.

PDF page 10 - College #21 complete data:
1 B TECH IN AERONAUTICAL ENGINEERING         60  60  3  0  5  52  57  3
2 B TECH IN COMPUTER SCIENCE AND ENGINEERING 120 120  6  1  9 104 113  6
3 B TECH IN COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE) 60 60 3 1 4 52 56 3
4 B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING 60 60 3 0 5 52 57 3
5 B TECH IN ELECTRONICS & COMPUTER ENGINEERING 60 60 3 1 5 51 56 3
6 B Tech in ROBOTICS AND ARTIFICIAL INTELLIGENCE 60 60 3 1 4 52 56 3   <- MISSING!
7 BTECH IN MECHANICAL AND SMART MANUFACTURING 30 30 2 0 2 26 28 2
Ins Total: 450 450 23 4 34 389 423 23

PDF page 10 - College #22 (VTU CPGS Kalburgi) complete data:
1 B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE 120 120 6 1 79 34 113 6
2 COMPUTER SCIENCE AND ENGINEERING           120 120  6  1  79  34 113  6
3 ELECTRONICS & COMPUTER ENGINEERING          60  60  3  0  40  17  57  3
Ins Total: 300 300 15 2 198 85 283 15
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# --- Fix College #21 ---
col21 = next(c for c in d["colleges"] if c["annexure"] == "A" and c["college_number"] == 21)
print(f"Before fix - #{col21['college_number']}: {len(col21['courses'])} courses, intake={col21['total_intake']}")

# Replace with full correct data from PDF
col21["courses"] = [
    {"course_name": "B TECH IN AERONAUTICAL ENGINEERING",
     "total_intake": 60, "total_kea_seats": 60, "snq_5pct": 3,
     "kea_ph": 3, "kea_spl": 0, "kea_hk": 5, "kea_rk": 52, "kea_tot": 57, "over_above_5pct": 3,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "B TECH IN COMPUTER SCIENCE AND ENGINEERING",
     "total_intake": 120, "total_kea_seats": 120, "snq_5pct": 6,
     "kea_ph": 6, "kea_spl": 1, "kea_hk": 9, "kea_rk": 104, "kea_tot": 113, "over_above_5pct": 6,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "B TECH IN COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",
     "total_intake": 60, "total_kea_seats": 60, "snq_5pct": 3,
     "kea_ph": 3, "kea_spl": 1, "kea_hk": 4, "kea_rk": 52, "kea_tot": 56, "over_above_5pct": 3,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",
     "total_intake": 60, "total_kea_seats": 60, "snq_5pct": 3,
     "kea_ph": 3, "kea_spl": 0, "kea_hk": 5, "kea_rk": 52, "kea_tot": 57, "over_above_5pct": 3,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "B TECH IN ELECTRONICS & COMPUTER ENGINEERING",
     "total_intake": 60, "total_kea_seats": 60, "snq_5pct": 3,
     "kea_ph": 3, "kea_spl": 1, "kea_hk": 5, "kea_rk": 51, "kea_tot": 56, "over_above_5pct": 3,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",
     "total_intake": 60, "total_kea_seats": 60, "snq_5pct": 3,
     "kea_ph": 3, "kea_spl": 1, "kea_hk": 4, "kea_rk": 52, "kea_tot": 56, "over_above_5pct": 3,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "BTECH IN MECHANICAL AND SMART MANUFACTURING",
     "total_intake": 30, "total_kea_seats": 30, "snq_5pct": 2,
     "kea_ph": 2, "kea_spl": 0, "kea_hk": 2, "kea_rk": 26, "kea_tot": 28, "over_above_5pct": 2,
     "cat2_seats": 0, "cat3_seats": 0},
]
col21["total_intake"] = 450
col21["total_kea_seats"] = 450

# --- Fix College #22 (VTU CPGS Kalburgi) - has HK-heavy seats (different from norm) ---
col22 = next(c for c in d["colleges"] if c["annexure"] == "A" and c["college_number"] == 22)
print(f"Before fix - #{col22['college_number']}: {len(col22['courses'])} courses, intake={col22['total_intake']}")
col22["courses"] = [
    {"course_name": "B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",
     "total_intake": 120, "total_kea_seats": 120, "snq_5pct": 6,
     "kea_ph": 6, "kea_spl": 1, "kea_hk": 79, "kea_rk": 34, "kea_tot": 113, "over_above_5pct": 6,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "COMPUTER SCIENCE AND ENGINEERING",
     "total_intake": 120, "total_kea_seats": 120, "snq_5pct": 6,
     "kea_ph": 6, "kea_spl": 1, "kea_hk": 79, "kea_rk": 34, "kea_tot": 113, "over_above_5pct": 6,
     "cat2_seats": 0, "cat3_seats": 0},
    {"course_name": "ELECTRONICS & COMPUTER ENGINEERING",
     "total_intake": 60, "total_kea_seats": 60, "snq_5pct": 3,
     "kea_ph": 3, "kea_spl": 0, "kea_hk": 40, "kea_rk": 17, "kea_tot": 57, "over_above_5pct": 3,
     "cat2_seats": 0, "cat3_seats": 0},
]
col22["total_intake"] = 300
col22["total_kea_seats"] = 300

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"After fix  - #21: {len(col21['courses'])} courses, intake={col21['total_intake']}")
print(f"After fix  - #22: {len(col22['courses'])} courses, intake={col22['total_intake']}")

# Final verification against PDF totals
PDF_TOTALS = {
    "total_intake": 6255, "total_kea": 6255,
    "kea_ph": 313, "kea_spl": 68, "kea_hk": 1394,
    "kea_rk": 4480, "kea_tot": 5874, "over_above_5pct": 313,
}

ann_a = [c for c in d["colleges"] if c["annexure"] == "A"]
sums = {k: 0 for k in PDF_TOTALS}
for college in ann_a:
    for c in college["courses"]:
        sums["total_intake"]    += c.get("total_intake", 0)
        sums["total_kea"]       += c.get("total_kea_seats", 0)
        sums["kea_ph"]          += c.get("kea_ph", 0)
        sums["kea_spl"]         += c.get("kea_spl", 0)
        sums["kea_hk"]          += c.get("kea_hk", 0)
        sums["kea_rk"]          += c.get("kea_rk", 0)
        sums["kea_tot"]         += c.get("kea_tot", 0)
        sums["over_above_5pct"] += c.get("over_above_5pct", 0)

LABELS = {
    "total_intake": "Total Intake", "total_kea": "Total KEA",
    "kea_ph": "PH 5%", "kea_spl": "SPL", "kea_hk": "HK",
    "kea_rk": "RK", "kea_tot": "TOT HK-RK", "over_above_5pct": "Over SNQ 5%",
}

print()
print("-" * 58)
print("  ANNEXURE A FINAL VERIFICATION vs PDF Grand Total")
print("-" * 58)
print(f"  {'Field':<20} {'PDF':>7} {'Ours':>7} {'Diff':>7}  Status")
print("-" * 58)
all_ok = True
for k, label in LABELS.items():
    pv = PDF_TOTALS[k]
    ov = sums[k]
    diff = ov - pv
    ok = "OK" if diff == 0 else f"OFF {diff:+d}"
    if diff != 0:
        all_ok = False
    marker = "" if diff == 0 else "  <---"
    print(f"  {label:<20} {pv:>7} {ov:>7} {diff:>+7}  {ok}{marker}")
print("-" * 58)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'Still mismatches'}")
print(f"  Colleges: {len(ann_a)}/23")
