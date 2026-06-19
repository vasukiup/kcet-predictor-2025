"""
Rebuild Annexure B completely from PDF text (colleges 1-6).
Colleges 7 & 8 are on image-only page 15 - will be added as stubs.

Annexure B column layout (different from A!):
  Total Intake | Total KEA (95%) | PH 5% | SPL | HK | RK | TOT HK-RK | CAT-3 MGMT 5% | Over & Above SNQ 5%
  
So there is an extra column: CAT-3 Management seats (5%)
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Remove ALL existing Annexure B colleges so we rebuild cleanly
d["colleges"] = [c for c in d["colleges"] if c["annexure"] != "B"]

def make_college(num, name, address, district, courses_data):
    courses = []
    for cn, intake, kea, ph, spl, hk, rk, tot, cat3, over in courses_data:
        courses.append({
            "course_name": cn,
            "total_intake": intake,
            "total_kea_seats": kea,
            "snq_5pct": over,          # Over & Above SNQ 5% = snq_5pct
            "kea_ph": ph,
            "kea_spl": spl,
            "kea_hk": hk,
            "kea_rk": rk,
            "kea_tot": tot,
            "cat3_mgmt": cat3,
            "over_above_5pct": over,
            "cat2_seats": 0,
            "cat3_seats": cat3,
        })
    return {
        "college_number": num,
        "college_name": name,
        "address": address,
        "annexure": "B",
        "college_type": "Government Aided Private Colleges",
        "district": district,
        "cat1_pct": 95,
        "cat2_pct": 0,
        "cat3_pct": 5,
        "total_intake": sum(c["total_intake"] for c in courses),
        "total_kea_seats": sum(c["total_kea_seats"] for c in courses),
        "courses": courses,
    }

# fmt: intake kea ph spl hk rk tot cat3 over
ann_b_colleges = [
    make_college(1,
        "B M S College of Engineering, Basavanagudi, Bangalore (AUTONOMOUS)",
        "POST BOX NO 1908, BULL TEMPLE ROAD, BANGALORE", "Bangalore",
        [
            ("CIVIL ENGINEERING",                           60, 57, 3, 0, 4, 50, 54, 3, 3),
            ("ELECTRICAL & ELECTRONICS ENGINEERING",        60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRONICS AND COMMUNICATION ENGG",         60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("INDUSTRIAL ENGINEERING & MANAGEMENT",         60, 57, 2, 0, 5, 50, 55, 3, 3),
            ("MECHANICAL ENGINEERING",                      60, 57, 3, 0, 5, 49, 54, 3, 3),
        ]),
    make_college(2,
        "B V V Sangha's Basaveshwara Engineering College, Bagalkote (AUTONOMOUS)",
        "NIJALINGAPPA ROAD, BAGALKOT 587102", "Bagalkot",
        [
            ("CIVIL ENGINEERING",                           90, 85, 4, 1, 7, 73, 80, 5, 5),
            ("COMPUTER SCIENCE AND ENGINEERING",            60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRICAL & ELECTRONICS ENGINEERING",        60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRONICS AND COMMUNICATION ENGG",         60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("INDUSTRIAL & PRODUCTION ENGINEERING",         30, 29, 1, 0, 2, 26, 28, 1, 1),
            ("MECHANICAL ENGINEERING",                     120,114, 6, 1, 9, 98,107, 6, 6),
        ]),
    make_college(3,
        "Dr. Ambedkar Institute of Technology, Bangalore (AUTONOMOUS)",
        "OUTER RING ROAD, NEAR JNANA BHARATHI CAMPUS, MALLATHAHALLI, BANGALORE-560056", "Bangalore",
        [
            ("CIVIL ENGINEERING",                           90, 85, 4, 1, 7, 73, 80, 5, 5),
            ("COMPUTER SCIENCE AND ENGINEERING",            60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRICAL & ELECTRONICS ENGINEERING",        60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRONICS AND COMMUNICATION ENGG",        120,114, 5, 1, 9, 99,108, 6, 6),
            ("ELECTRONICS AND INSTRUMENTATION ENGINEERING", 60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRONICS AND TELECOMMUNICATION ENGINEERING",60,57, 3, 0, 4, 50, 54, 3, 3),
            ("INDUSTRIAL ENGINEERING & MANAGEMENT",         30, 29, 1, 0, 2, 26, 28, 1, 1),
            ("MECHANICAL ENGINEERING",                     120,114, 6, 1, 9, 98,107, 6, 6),
        ]),
    make_college(4,
        "Malnad College of Engineering, Hassan (AUTONOMOUS)",
        "P.B. NO. 21, SALAGAME ROAD, HASSAN", "Hassan",
        [
            ("CIVIL ENGINEERING",                           60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRICAL & ELECTRONICS ENGINEERING",        60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("ELECTRONICS AND COMMUNICATION ENGG",         60, 57, 3, 0, 4, 50, 54, 3, 3),
            ("MECHANICAL ENGINEERING",                     120,114, 5, 1, 9, 99,108, 6, 6),
        ]),
    make_college(5,
        "P D A College of Engineering, Gulbarga (AUTONOMOUS)",
        "AIWAN-E-SHAHI AREA, STATION ROAD, GULBARGA-585102", "Gulbarga",
        [
            ("CIVIL ENGINEERING",                           90, 86, 4, 1, 57, 24, 81, 4, 4),
            ("ELECTRICAL & ELECTRONICS ENGINEERING",        40, 38, 2, 0, 25, 11, 36, 2, 2),
            ("ELECTRONICS AND COMMUNICATION ENGG",         60, 57, 3, 0, 38, 16, 54, 3, 3),
            ("INDUSTRIAL & PRODUCTION ENGINEERING",         40, 38, 2, 0, 25, 11, 36, 2, 2),
            ("MECHANICAL ENGINEERING",                      90, 85, 4, 1, 56, 24, 80, 5, 5),
        ]),
    make_college(6,
        "P E S College of Engineering, Mandya (AUTONOMOUS)",
        "MANDYA: 571 401", "Mandya",
        [
            ("CIVIL ENGINEERING",                           90, 86, 4, 1, 6, 75, 81, 4, 5),
            ("ELECTRICAL & ELECTRONICS ENGINEERING",        40, 38, 2, 0, 3, 33, 36, 2, 2),
            ("ELECTRONICS AND COMMUNICATION ENGG",         60, 57, 3, 1, 4, 49, 53, 3, 3),
            ("MECHANICAL ENGINEERING",                     120,114, 6, 1, 9, 98,107, 6, 6),
        ]),
]

d["colleges"].extend(ann_b_colleges)

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

# Print summary
ann_b = [c for c in d["colleges"] if c["annexure"] == "B"]
print(f"Annexure B rebuilt: {len(ann_b)} colleges (+ 2 on image page)")
print()
for col in ann_b:
    n_courses = len(col["courses"])
    ti = col["total_intake"]
    tk = col["total_kea_seats"]
    print(f"  #{col['college_number']:>2} {col['college_name'][:55]:<55} | courses={n_courses} | intake={ti:>4} | kea={tk:>4}")
print()

# Summed totals
t_intake = sum(c["total_intake"] for c in ann_b)
t_kea    = sum(c["total_kea_seats"] for c in ann_b)
t_ph     = sum(cr["kea_ph"] for c in ann_b for cr in c["courses"])
t_spl    = sum(cr["kea_spl"] for c in ann_b for cr in c["courses"])
t_hk     = sum(cr["kea_hk"] for c in ann_b for cr in c["courses"])
t_rk     = sum(cr["kea_rk"] for c in ann_b for cr in c["courses"])
t_tot    = sum(cr["kea_tot"] for c in ann_b for cr in c["courses"])
t_cat3   = sum(cr.get("cat3_mgmt",0) for c in ann_b for cr in c["courses"])
t_over   = sum(cr["over_above_5pct"] for c in ann_b for cr in c["courses"])

print(f"  Colleges 1-6 subtotals (excl. image-page colleges 7 & 8):")
print(f"  Total Intake : {t_intake}")
print(f"  Total KEA    : {t_kea}")
print(f"  PH 5%        : {t_ph}")
print(f"  SPL          : {t_spl}")
print(f"  HK           : {t_hk}")
print(f"  RK           : {t_rk}")
print(f"  TOT HK-RK    : {t_tot}")
print(f"  CAT-3 MGMT   : {t_cat3}")
print(f"  Over SNQ 5%  : {t_over}")
print()
print("  NOTE: Colleges #7 and #8 are on image-only page 15.")
print("  Grand total from PDF needed to derive their seat counts.")
