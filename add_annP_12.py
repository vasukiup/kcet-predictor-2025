import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Helper to create course records
def cr(name, intake, kea, ph, spl, hk, rk, tot):
    return {"course_name":name, "total_intake":intake, "total_kea_seats":kea,
            "snq_5pct":0, "kea_ph":ph, "kea_spl":spl, "kea_hk":hk, "kea_rk":rk,
            "kea_tot":tot, "cat2_seats":0, "cat3_seats":0, "over_above_5pct":0}

def col(num, name, addr, dist, cat1, courses):
    return {"college_number":num, "college_name":name, "address":addr,
            "annexure":"P", "college_type":"Deemed University",
            "district":dist, "cat1_pct":cat1, "cat2_pct":0, "cat3_pct":0,
            "total_intake":sum(c["total_intake"] for c in courses),
            "total_kea_seats":sum(c["total_kea_seats"] for c in courses),
            "courses":courses}

ann_p_colleges = [
  col(1,"GANDHI INSTITUTE OF TECHNOLOGY AND MANAGEMENT (GITAM) OFF CAMPUS BENGALURU",
      "NH 207, NAGADENEHALLI, DODDABALLAPUR TALUK, BENGALURU-561203","Bangalore",28,[
    cr("CIVIL ENGINEERING WITH COMPUTER APPLICATION",  30, 12,1,0, 1,10,11),
    cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",360,90,5,1, 7,77,84),
    cr("COMPUTER SCIENCE AND ENGINEERING",             420,105,5,1, 8,91,99),
    cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",60,15,1,0, 1,13,14),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",  120,30,1,1, 2,26,28),
    cr("ELECTRICAL & COMPUTER ENGINEERING",             30, 12,0,0, 1,11,12),
    cr("ELECTRONICS ENGINEERING (VLSI DESIGN & TECHNOLOGY)",30,12,1,1, 1, 9,10),
    cr("ELECTRONICS AND COMMUNICATION ENGG",           120, 48,2,1, 3,42,45),
    cr("MECHANICAL ENGINEERING",                        30, 12,1,0, 1,10,11),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",          30,  8,0,0, 1, 7, 8),
  ]),
  col(2,"Sri Siddhartha Institute of Technology",
      "MARALUR, TUMKUR","Tumkur",40,[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",  60, 24,1,0, 2,21,23),
    cr("BIO-MEDICAL ENGINEERING",                       30, 12,1,0, 1,10,11),
    cr("CIVIL ENGINEERING",                             60, 24,1,0, 2,21,23),
    cr("COMPUTER SCIENCE AND ENGINEERING",             180, 72,4,1, 5,62,67),
    cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",60,24,1,0,2,21,23),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",  60,24,1,0,2,21,23),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",         120, 48,3,1, 3,41,44),
    cr("ELECTRONICS AND COMMUNICATION ENGG",           180, 72,4,1, 5,62,67),
    cr("ELECTRONICS AND TELECOMMUNICATION ENGINEERING", 60, 24,1,0, 2,21,23),
    cr("INFORMATION SCIENCE AND ENGINEERING",          120, 48,2,1, 4,41,45),
    cr("MECHANICAL ENGINEERING",                        60, 24,1,0, 2,21,23),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",          60, 24,1,0, 2,21,23),
  ]),
]

d["colleges"] = [c for c in d["colleges"] if c["annexure"] != "P"]
d["colleges"].extend(ann_p_colleges)

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Added Gitam (P-1) and Sri Siddhartha (P-2) to Annexure P baseline.")
