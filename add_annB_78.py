"""
Add colleges #7 and #8 from Annexure B (read from page 15 image).

College #7: Sri Jayachamarajendra College of Engineering (Constituent College of JSS Science & Technology University), Mysore
Address: JSS TECHNICAL INSTITUTIONS CAMPUS, MANASAGANGOTHRI PO, MYSORE
Courses:
1  CIVIL ENGINEERING                      60  57  3  1  4  49  53  3  3
2  COMPUTER SCIENCE AND ENGINEERING       60  57  3  1  4  49  53  3  3
3  ELECTRICAL & ELECTRONICS ENGINEERING   60  57  3  1  4  49  53  3  3
4  ELECTRONICS & INSTRUMENTATION ENGG     60  57  3  1  4  49  53  3  3
5  ELECTRONICS AND COMMUNICATION ENGG     60  57  3  0  5  49  54  3  3
6  ENVIRONMENTAL ENGINEERING              60  57  3  1  4  49  53  3  3
7  INDUSTRIAL & PRODUCTION ENGINEERING    60  57  3  0  4  50  54  3  3
8  MECHANICAL ENGINEERING                 60  57  2  1  5  49  54  3  3
9  POLYMER SCIENCE & TECHNOLOGY           40  38  2  0  3  33  36  2  2
Ins Total: 520 494 25 6 37 426 463 26 26

College #8: The National Institute of Engineering, Mysore (AUTONOMOUS)
Address: MANANDAVADI ROAD, MYSORE
Courses:
1  CIVIL ENGINEERING                      60  57  3  1  5  48  53  3  3
2  ELECTRONICS AND COMMUNICATION ENGG     60  57  3  1  4  49  53  3  3
3  MECHANICAL ENGINEERING                 60  57  3  1  4  49  53  3  3
Ins Total: 180 171 9 3 13 146 159 9 9

TOTAL: Annexure-B = 2950 | 2803 | 140 | 30 | 389 | 2244 | 2633 | 147 | 148
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

def make_courses(rows):
    return [
        {
            "course_name": cn,
            "total_intake": intake, "total_kea_seats": kea,
            "snq_5pct": over, "kea_ph": ph, "kea_spl": spl,
            "kea_hk": hk, "kea_rk": rk, "kea_tot": tot,
            "cat3_mgmt": cat3, "over_above_5pct": over,
            "cat2_seats": 0, "cat3_seats": cat3,
        }
        for cn, intake, kea, ph, spl, hk, rk, tot, cat3, over in rows
    ]

col7_courses = make_courses([
    ("CIVIL ENGINEERING",                        60, 57, 3, 1, 4, 49, 53, 3, 3),
    ("COMPUTER SCIENCE AND ENGINEERING",         60, 57, 3, 1, 4, 49, 53, 3, 3),
    ("ELECTRICAL & ELECTRONICS ENGINEERING",     60, 57, 3, 1, 4, 49, 53, 3, 3),
    ("ELECTRONICS & INSTRUMENTATION ENGINEERING",60, 57, 3, 1, 4, 49, 53, 3, 3),
    ("ELECTRONICS AND COMMUNICATION ENGG",       60, 57, 3, 0, 5, 49, 54, 3, 3),
    ("ENVIRONMENTAL ENGINEERING",                60, 57, 3, 1, 4, 49, 53, 3, 3),
    ("INDUSTRIAL & PRODUCTION ENGINEERING",      60, 57, 3, 0, 4, 50, 54, 3, 3),
    ("MECHANICAL ENGINEERING",                   60, 57, 2, 1, 5, 49, 54, 3, 3),
    ("POLYMER SCIENCE & TECHNOLOGY",             40, 38, 2, 0, 3, 33, 36, 2, 2),
])

col8_courses = make_courses([
    ("CIVIL ENGINEERING",                  60, 57, 3, 1, 5, 48, 53, 3, 3),
    ("ELECTRONICS AND COMMUNICATION ENGG", 60, 57, 3, 1, 4, 49, 53, 3, 3),
    ("MECHANICAL ENGINEERING",             60, 57, 3, 1, 4, 49, 53, 3, 3),
])

new_colleges = [
    {
        "college_number": 7,
        "college_name": "Sri Jayachamarajendra College of Engineering (Constituent College of JSS Science & Technology University), Mysore",
        "address": "JSS TECHNICAL INSTITUTIONS CAMPUS, MANASAGANGOTHRI PO, MYSORE",
        "annexure": "B",
        "college_type": "Government Aided Private Colleges",
        "district": "Mysore",
        "cat1_pct": 95, "cat2_pct": 0, "cat3_pct": 5,
        "total_intake": 520,
        "total_kea_seats": 494,
        "courses": col7_courses,
    },
    {
        "college_number": 8,
        "college_name": "The National Institute of Engineering, Mysore (AUTONOMOUS)",
        "address": "MANANDAVADI ROAD, MYSORE",
        "annexure": "B",
        "college_type": "Government Aided Private Colleges",
        "district": "Mysore",
        "cat1_pct": 95, "cat2_pct": 0, "cat3_pct": 5,
        "total_intake": 180,
        "total_kea_seats": 171,
        "courses": col8_courses,
    },
]

d["colleges"].extend(new_colleges)

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

# ── Verify against PDF Grand Total ─────────────────────────────────────
PDF_TOTAL = {
    "total_intake": 2950, "total_kea": 2803,
    "kea_ph": 140, "kea_spl": 30, "kea_hk": 389,
    "kea_rk": 2244, "kea_tot": 2633,
    "cat3_mgmt": 147, "over_above_5pct": 148,
}

ann_b = sorted([c for c in d["colleges"] if c["annexure"] == "B"], key=lambda x: x["college_number"])
sums = {k: 0 for k in PDF_TOTAL}
for college in ann_b:
    for c in college["courses"]:
        sums["total_intake"]    += c.get("total_intake", 0)
        sums["total_kea"]       += c.get("total_kea_seats", 0)
        sums["kea_ph"]          += c.get("kea_ph", 0)
        sums["kea_spl"]         += c.get("kea_spl", 0)
        sums["kea_hk"]          += c.get("kea_hk", 0)
        sums["kea_rk"]          += c.get("kea_rk", 0)
        sums["kea_tot"]         += c.get("kea_tot", 0)
        sums["cat3_mgmt"]       += c.get("cat3_mgmt", 0)
        sums["over_above_5pct"] += c.get("over_above_5pct", 0)

LABELS = {
    "total_intake": "Total Intake", "total_kea": "Total KEA (95%)",
    "kea_ph": "PH 5%", "kea_spl": "SPL", "kea_hk": "HK",
    "kea_rk": "RK", "kea_tot": "TOT HK-RK",
    "cat3_mgmt": "CAT-3 MGMT 5%", "over_above_5pct": "Over SNQ 5%",
}

SEP = "-" * 62
print(SEP)
print("  ANNEXURE B FINAL VERIFICATION vs PDF Grand Total")
print(SEP)
print(f"  {'Field':<22} {'PDF':>7} {'Ours':>7} {'Diff':>7}  Status")
print(SEP)
all_ok = True
for k, label in LABELS.items():
    pv = PDF_TOTAL[k]; ov = sums[k]; diff = ov - pv
    ok = "OK" if diff == 0 else f"OFF {diff:+d}"
    if diff != 0: all_ok = False
    marker = "  <---" if diff != 0 else ""
    print(f"  {label:<22} {pv:>7} {ov:>7} {diff:>+7}  {ok}{marker}")
print(SEP)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'STILL HAS MISMATCHES'}")
print(f"  Colleges: {len(ann_b)}/8")
print()
for col in ann_b:
    print(f"  #{col['college_number']:>2} {col['college_name'][:58]:<58} | intake={col['total_intake']:>4} | kea={col['total_kea_seats']:>4}")
