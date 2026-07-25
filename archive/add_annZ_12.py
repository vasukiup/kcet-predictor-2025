import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

def make_courses(rows):
    return [
        {
            "course_name": cn,
            "total_intake": intake, "total_kea_seats": kea,
            "snq_5pct": over, "kea_ph": ph, "kea_spl": spl,
            "kea_hk": hk, "kea_rk": rk, "kea_tot": hk + rk,
            "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": over,
        }
        for cn, intake, kea, ph, spl, hk, rk, over in rows
    ]

# Chintamani Annexure Z courses
chintamani_z_courses = make_courses([
    ("COMPUTER SCIENCE AND ENGINEERING",                30, 30, 2, 0, 2, 26, 1),
    ("COMPUTER SCIENCE AND ENGINEERING (AIML)",        30, 30, 2, 1, 2, 25, 1),
    ("ELECTRICAL & ELECTRONICS ENGINEERING",            30, 30, 1, 0, 2, 27, 2),
    ("ELECTRONICS AND COMMUNICATION ENGG",              30, 30, 1, 0, 3, 26, 2),
])

# UBDT Annexure Z courses
ubdt_z_courses = make_courses([
    ("CIVIL ENGINEERING",                               30, 30, 1, 0, 2, 27, 2),
    ("COMPUTER SCIENCE AND ENGINEERING",                60, 60, 3, 1, 5, 51, 3),
    ("ELECTRICAL & ELECTRONICS ENGINEERING",            30, 30, 1, 0, 2, 27, 2),
    ("ELECTRONICS AND COMMUNICATION ENGG",              60, 60, 3, 1, 5, 51, 3),
    ("ELECTRONICS AND INSTRUMENTATION ENGINEERING",     30, 30, 2, 0, 2, 26, 1),
    ("MECHANICAL ENGINEERING",                          35, 35, 2, 1, 3, 29, 2),
    ("ROBOTICS AND ARTIFICIAL INTELLIGENCE",            30, 30, 2, 0, 2, 26, 1),
])

new_z_colleges = [
    {
        "college_number": 1,
        "college_name": "Constituent College of VTU, Chintamani Chikaballapura",
        "address": "DIST CHIKBALLAPURA",
        "annexure": "Z",
        "college_type": "Government (Higher Fees)",
        "district": "Chikkaballapura",
        "cat1_pct": 100, "cat2_pct": 0, "cat3_pct": 0,
        "total_intake": 120,
        "total_kea_seats": 120,
        "kea_code": "E309",
        "courses": chintamani_z_courses,
    },
    {
        "college_number": 2,
        "college_name": "University B.D.T College of Engineering, Davanagere",
        "address": "P J EXTENSION, HADADI ROAD, DAVENGERE",
        "annexure": "Z",
        "college_type": "Government (Higher Fees)",
        "district": "Davanagere",
        "cat1_pct": 100, "cat2_pct": 0, "cat3_pct": 0,
        "total_intake": 275,
        "total_kea_seats": 275,
        "kea_code": "E066",
        "courses": ubdt_z_courses,
    },
]

# Clean up any existing Z colleges (just to be safe)
d["colleges"] = [c for c in d["colleges"] if c["annexure"] != "Z"]
d["colleges"].extend(new_z_colleges)

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Added Chintamani (Z-1) and UBDT (Z-2) to Annexure Z baseline.")
