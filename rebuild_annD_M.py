"""
Complete rebuild of Annexure D (16 minority colleges) and add Annexure M.
Purges all bad data from DB and replaces with correct values.

Annexure D column layout (Private Minority):
  Total Intake | Total KEA (40%) | PH 5% | SPL | HK | RK | TOT HK-RK | CAT-2 KRLMPCA/AMPCA 30% | CAT-3 MGMT 30% | Over SNQ 5%

NOTE: The mislabeled colleges (universities etc.) that were in "D" belong to other annexures.
We strip them all out and rebuild from scratch using only the 16 colleges confirmed in PDF pages 94-101.

Grand total:  10440 | 4176 | 209 | 46 | 559 | 3362 | 3921 | 3132 | 3132 | 522

Annexure M (page 103 image):
  1 University of Visvesvaraya College of Engineering (A State Autonomous Public University on IIT Model)
  Address: K R Circle, Bangalore
  CAT-1 = 100%, no CAT-2/CAT-3
  Total: 760 | 760 | 38 | 7 | 57 | 658 | 715
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Remove all existing Annexure D and M colleges
before = len(d["colleges"])
d["colleges"] = [c for c in d["colleges"] if c["annexure"] not in ("D", "M")]
after = len(d["colleges"])
print(f"Removed {before - after} existing Annexure D/M records")

# ── Helper ──────────────────────────────────────────────────────────────────
def c_row(name, intake, kea, ph, spl, hk, rk, tot, cat2, cat3, over):
    return {
        "course_name": name, "total_intake": intake, "total_kea_seats": kea,
        "snq_5pct": over, "kea_ph": ph, "kea_spl": spl,
        "kea_hk": hk, "kea_rk": rk, "kea_tot": tot,
        "cat2_seats": cat2, "cat3_seats": cat3, "over_above_5pct": over,
    }

def college(num, name, addr, dist, courses):
    return {
        "college_number": num, "college_name": name, "address": addr,
        "annexure": "D", "college_type": "Private Unaided Minority Colleges",
        "district": dist, "cat1_pct": 40, "cat2_pct": 30, "cat3_pct": 30,
        "total_intake": sum(c["total_intake"] for c in courses),
        "total_kea_seats": sum(c["total_kea_seats"] for c in courses),
        "courses": courses,
    }

# ── Annexure D: 16 Colleges ──────────────────────────────────────────────────
ann_d = [
    college(1, "A J Institute Of Engineering And Technology, Mangalore",
        "KOTTAR CHOWKI, MANGALORE", "Dakshina Kannada", [
        c_row("CIVIL ENGINEERING",                          60, 24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",          120, 48,2,1, 3,42,45,36,36,6),
        c_row("COMPUTER SCIENCE AND ENGINEERING (AI/ML)",   60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                    120, 48,2,1, 3,42,45,36,36,6),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41,45,36,36,6),
        c_row("COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS ENGINEERING (VLSI DESIGN)",      60, 24,1,0, 2,21,23,18,18,3),
    ]),
    college(2, "Anjuman Institute of Technology & Management, Bhatkal",
        "BHATKAL", "Uttara Kannada", [
        c_row("CIVIL ENGINEERING",                          30, 12,1,0, 1,10,11, 9, 9,1),
        c_row("COMPUTER SCIENCE AND ENGINEERING",          120, 48,2,1, 3,42,45,36,36,6),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21,23,18,18,3),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0, 2,21,23,18,18,3),
    ]),
    college(3, "Bahubali College of Engineering, Shravanabelagola, Hassan",
        "SHRAVANABELAGOLA, HASSAN", "Hassan", [
        c_row("CIVIL ENGINEERING",                          30, 12,1,0, 1,10,11, 9, 9,1),
        c_row("COMPUTER SCIENCE AND ENGINEERING",           60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21,23,18,18,3),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        30, 12,1,0, 1,10,11, 9, 9,2),
    ]),
    college(4, "Beary's Institute of Technology, Boliar Village, Bantwal Tq, Mangalore",
        "BOLIAR VILLAGE, BANTWAL TQ, MANGALORE", "Dakshina Kannada", [
        c_row("COMPUTER SCIENCE AND ENGINEERING",           60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21,23,18,18,3),
        c_row("CIVIL ENGINEERING",                          60, 24,1,0, 2,21,23,18,18,3),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        30, 12,1,0, 1,10,11, 9, 9,1),
    ]),
    college(5, "Canara Engineering College, Bantwal",
        "BANTWAL", "Dakshina Kannada", [
        c_row("CIVIL ENGINEERING",                         120, 48,2,1, 8,37,45,36,36,6),
        c_row("COMPUTER SCIENCE AND ENGINEERING",          120, 48,2,1, 3,42,45,36,36,6),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 8,37,45,36,36,6),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",        120, 48,2,1, 8,37,45,36,36,6),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        60, 24,1,0, 4,19,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                    120, 48,2,1, 8,37,45,36,36,6),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",90,36,2,1, 6,27,33,27,27,4),
    ]),
    college(6, "Ghousia Engineering College, Ramanagara",
        "RAMANAGARA", "Ramanagara", [
        c_row("CIVIL ENGINEERING",                          30, 12,1,0, 1,10,11, 9, 9,2),
        c_row("COMPUTER SCIENCE AND ENGINEERING",           60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 4,19,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0, 4,19,23,18,18,3),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                     60, 24,1,0, 4,19,23,18,18,3),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING (DS)",      90, 36,2,0, 6,28,34,27,27,4),
    ]),
    college(7, "Gurunanak Dev Engineering College, Bidar",
        "BIDAR", "Bidar", [
        c_row("CIVIL ENGINEERING",                          60, 24,1,0,16, 7,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",           90, 36,2,1,23,10,33,27,27,5),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0,16, 7,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                     60, 24,1,0,16, 7,23,18,18,3),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0,16, 7,23,18,18,3),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,0,16, 7,23,18,18,3),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        60, 24,1,0,16, 7,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0,16, 7,23,18,18,3),
        c_row("ELECTRONICS ENGINEERING (VLSI)",             60, 24,1,0,16, 7,23,18,18,3),
        c_row("COMPUTER SCIENCE AND BUSINESS SYSTEMS",      60, 24,1,0,16, 7,23,18,18,3),
    ]),
    college(8, "H.K.B.K. College of Engineering, Bangalore",
        "BANGALORE", "Bangalore", [
        c_row("COMPUTER SCIENCE AND ENGINEERING",          240, 96,5,1, 7,83,90,72,72,12),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",180,72,4,1,5,62,67,54,54,9),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",        180, 72,4,1, 5,62,67,54,54,9),
        c_row("INFORMATION SCIENCE AND ENGINEERING",       120, 48,2,1, 4,41,45,36,36,6),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41,45,36,36,6),
    ]),
    college(9, "K C T Engineering College, Gulbarga",
        "GULBARGA", "Gulbarga", [
        c_row("CIVIL ENGINEERING",                          60, 24,1,0,16, 7,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",           90, 36,2,1,23,10,33,27,27,5),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         60, 24,1,0,16, 7,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                     60, 24,1,0,16, 7,23,18,18,3),
    ]),
    college(10, "M V J College of Engineering, Bangalore (AUTONOMOUS)",
        "NEAR ITPB, CHANNASANDRA, KADUGODI POST, BANGALORE", "Bangalore", [
        c_row("AERO SPACE ENGINEERING",                      60, 24,1,0, 2,21,23,18,18,3),
        c_row("AERONAUTICAL ENGINEERING",                   120, 48,2,1, 3,42,45,36,36,6),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,0, 2,21,23,18,18,3),
        c_row("CHEMICAL ENGINEERING",                        30, 12,1,0, 1,10,11, 9, 9,2),
        c_row("CIVIL ENGINEERING",                           30, 12,1,0, 1,10,11, 9, 9,2),
        c_row("COMPUTER SCIENCE AND DESIGN",                 60, 24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",           240, 96,5,1, 7,83,90,72,72,12),
        c_row("COMPUTER SCIENCE AND ENGINEERING (DS)",       60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",        30, 12,1,0, 1,10,11, 9, 9,1),
        c_row("ELECTRONICS ENGINEERING (VLSI DESIGN)",       60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION (ADVANCED)",    60, 24,1,1, 2,20,22,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         180, 72,4,1, 5,62,67,54,54,9),
        c_row("INDUSTRIAL IOT",                              30, 12,0,0, 1,11,12, 9, 9,2),
        c_row("INFORMATION SCIENCE AND ENGINEERING",        120, 48,2,1, 3,42,45,36,36,6),
        c_row("MECHANICAL ENGINEERING",                      30, 12,1,0, 1,10,11, 9, 9,1),
    ]),
    college(11, "New Horizon College of Engineering, Varthur, Bangalore (AUTONOMOUS)",
        "RING ROAD, NEAR MARATHALLI, BELLANDUR POST, KADUBHISANAHALLI, BANGALORE", "Bangalore", [
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",180, 72,3,1, 5,63,68,54,54,9),
        c_row("COMPUTER SCIENCE AND ENGINEERING",           480,192,10,1,15,166,181,144,144,24),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",       120, 48,2,1, 4,41,45,36,36,6),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",         180, 72,4,1, 5,62,67,54,54,9),
        c_row("MECHANICAL ENGINEERING",                      60, 24,1,0, 2,21,23,18,18,3),
    ]),
    college(12, "P A College of Engineering, Kairangal, Bantwala Tq, Mangalore",
        "NADUPADAV, NEAR MANGALORE UNIVERSITY, MONTEPADAV POST, KAIRANGALA VILLAGE, BANTWAL-MANGALORE", "Dakshina Kannada", [
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING", 60, 24,1,0, 2,21,23,18,18,3),
        c_row("BIO-TECHNOLOGY",                               30, 12,1,0, 1,10,11, 9, 9,1),
        c_row("CIVIL ENGINEERING",                            30, 12,1,0, 1,10,11, 9, 9,2),
        c_row("COMPUTER SCIENCE AND ENGG (IoT & CYBER SEC)",  60, 24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",            120, 48,2,1, 3,42,45,36,36,6),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",           60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                       30, 12,1,0, 1,10,11, 9, 9,1),
    ]),
    college(13, "S D M Institute of Tech., Ujire, Dakshina Kannada",
        "UJIRE-574240 DAKSHINA KANNADA KARNATAKA", "Dakshina Kannada", [
        c_row("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",     60, 24,1,0, 2,21,23,18,18,3),
        c_row("CIVIL ENGINEERING",                            30, 12,1,0, 1,10,11, 9, 9,1),
        c_row("COMPUTER SCIENCE AND ENGINEERING",            120, 48,2,1, 3,42,45,36,36,6),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",         30, 12,1,0, 1,10,11, 9, 9,2),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",          120, 48,2,1, 4,41,45,36,36,6),
        c_row("INFORMATION SCIENCE AND ENGINEERING",          60, 24,1,0, 2,21,23,18,18,3),
    ]),
    college(14, "SDM College of Engineering, Dharwad (AUTONOMOUS)",
        "DHAVALAGIRI, KALGHATGI ROAD, DHARWAD", "Dharwad", [
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",  60, 24,1,0, 2,21,23,18,18,3),
        c_row("CHEMICAL ENGINEERING",                          30, 12,1,0, 1,10,11, 9, 9,1),
        c_row("CIVIL ENGINEERING",                             90, 36,2,1, 3,30,33,27,27,5),
        c_row("COMPUTER SCIENCE AND ENGINEERING",             120, 48,2,1, 4,41,45,36,36,6),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",          60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",           120, 48,2,1, 3,42,45,36,36,6),
        c_row("INFORMATION SCIENCE AND ENGINEERING",           60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHANICAL ENGINEERING",                       120, 48,3,1, 3,41,44,36,36,6),
    ]),
    college(15, "St. Joseph Engineering College, Mangalore (AUTONOMOUS)",
        "MANGALORE", "Dakshina Kannada", [
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",  60, 24,1,0, 2,21,23,18,18,3),
        c_row("CIVIL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND BUSINESS SYSTEMS",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",             240, 96,5,1, 7,83,90,72,72,12),
        c_row("COMPUTER SCIENCE AND ENGINEERING (DS)",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",          60, 24,1,1, 2,20,22,18,18,3),
        c_row("ELECTRONICS ENGINEERING (VLSI DESIGN)",         60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",           120, 48,3,1, 3,41,44,36,36,6),
        c_row("MECHANICAL ENGINEERING",                       120, 48,3,1, 3,41,44,36,36,6),
    ]),
    college(16, "The Oxford College of Engineering, Bangalore",
        "HOSUR ROAD, BOMMANAHALLI, BANGALORE", "Bangalore", [
        c_row("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",      60, 24,1,0, 2,21,23,18,18,3),
        c_row("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING", 120, 48,3,1, 3,41,44,36,36,6),
        c_row("BIO-TECHNOLOGY",                                60, 24,1,0, 2,21,23,18,18,3),
        c_row("CIVIL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
        c_row("COMPUTER SCIENCE AND ENGINEERING",             180, 72,4,1, 5,62,67,54,54,9),
        c_row("ELECTRICAL & ELECTRONICS ENGINEERING",          60, 24,1,0, 2,21,23,18,18,3),
        c_row("ELECTRONICS AND COMMUNICATION ENGG",           120, 48,3,1, 3,41,44,36,36,6),
        c_row("INFORMATION SCIENCE AND ENGINEERING",          120, 48,2,1, 4,41,45,36,36,6),
        c_row("MECHANICAL ENGINEERING",                        60, 24,1,0, 2,21,23,18,18,3),
        c_row("MECHATRONICS",                                  60, 24,1,0, 2,21,23,18,18,3),
    ]),
]
d["colleges"].extend(ann_d)
print(f"Added {len(ann_d)} Annexure D colleges")

# ── Annexure M: 1 College (from page 103 image) ──────────────────────────────
def m_row(name, intake, kea, ph, spl, hk, rk, tot):
    return {
        "course_name": name, "total_intake": intake, "total_kea_seats": kea,
        "snq_5pct": 0, "kea_ph": ph, "kea_spl": spl,
        "kea_hk": hk, "kea_rk": rk, "kea_tot": tot,
        "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 0,
    }

ann_m = [{
    "college_number": 1,
    "college_name": "University of Visvesvaraya College of Engineering (A State Autonomous Public University on IIT Model)",
    "address": "K R CIRCLE, BANGALORE",
    "annexure": "M",
    "college_type": "Government Public University",
    "district": "Bangalore",
    "cat1_pct": 100, "cat2_pct": 0, "cat3_pct": 0,
    "total_intake": 760, "total_kea_seats": 760,
    "courses": [
        m_row("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",  60, 60, 3,1, 4, 52, 56),
        m_row("CIVIL ENGINEERING",                        120,120, 6,1, 9,104,113),
        m_row("COMPUTER SCIENCE AND ENGINEERING",         120,120, 6,1, 9,104,113),
        m_row("ELECTRICAL & ELECTRONICS ENGINEERING",     120,120, 6,1, 9,104,113),
        m_row("ELECTRONICS AND COMMUNICATION ENGG",       120,120, 6,1, 9,104,113),
        m_row("INFORMATION SCIENCE AND ENGINEERING",       60, 60, 3,1, 5, 51, 56),
        m_row("MECHANICAL ENGINEERING",                   160,160, 8,1,12,139,151),
    ],
}]
d["colleges"].extend(ann_m)
print(f"Added {len(ann_m)} Annexure M college")

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

# ── Verify Annexure D against grand total ────────────────────────────────────
PDF_D = {"total_intake":10440,"total_kea":4176,"kea_ph":209,"kea_spl":46,
         "kea_hk":559,"kea_rk":3362,"kea_tot":3921,"cat2":3132,"cat3":3132,"over":522}

colleges_d = [c for c in d["colleges"] if c["annexure"] == "D"]
s = {k:0 for k in PDF_D}
for col in colleges_d:
    for c in col["courses"]:
        s["total_intake"] += c.get("total_intake",0)
        s["total_kea"]    += c.get("total_kea_seats",0)
        s["kea_ph"]       += c.get("kea_ph",0)
        s["kea_spl"]      += c.get("kea_spl",0)
        s["kea_hk"]       += c.get("kea_hk",0)
        s["kea_rk"]       += c.get("kea_rk",0)
        s["kea_tot"]      += c.get("kea_tot",0)
        s["cat2"]         += c.get("cat2_seats",0)
        s["cat3"]         += c.get("cat3_seats",0)
        s["over"]         += c.get("over_above_5pct",0)

LABS = {"total_intake":"Total Intake","total_kea":"Total KEA (40%)","kea_ph":"PH 5%",
        "kea_spl":"SPL","kea_hk":"HK","kea_rk":"RK","kea_tot":"TOT HK-RK",
        "cat2":"CAT-2 KRLMP 30%","cat3":"CAT-3 Mgmt 30%","over":"Over SNQ 5%"}

SEP = "-"*66
print(f"\n{SEP}")
print("  ANNEXURE D VERIFICATION vs PDF Grand Total")
print(SEP)
print(f"  {'Field':<22} {'PDF':>8} {'Ours':>8} {'Diff':>8}  Status")
print(SEP)
all_ok = True
for k,label in LABS.items():
    pv=PDF_D[k]; ov=s[k]; diff=ov-pv
    ok="OK" if diff==0 else f"OFF {diff:+d}"
    if diff!=0: all_ok=False
    print(f"  {label:<22} {pv:>8} {ov:>8} {diff:>+8}  {ok}{'  <---' if diff!=0 else ''}")
print(SEP)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'MISMATCHES - need tuning'}")
print(f"  Colleges: {len(colleges_d)}/16")

# ── Verify Annexure M ────────────────────────────────────────────────────────
PDF_M = {"total_intake":760,"total_kea":760,"kea_ph":38,"kea_spl":7,"kea_hk":57,"kea_rk":658,"kea_tot":715}
colleges_m = [c for c in d["colleges"] if c["annexure"] == "M"]
sm = {k:0 for k in PDF_M}
for col in colleges_m:
    for c in col["courses"]:
        sm["total_intake"] += c.get("total_intake",0)
        sm["total_kea"]    += c.get("total_kea_seats",0)
        sm["kea_ph"]       += c.get("kea_ph",0)
        sm["kea_spl"]      += c.get("kea_spl",0)
        sm["kea_hk"]       += c.get("kea_hk",0)
        sm["kea_rk"]       += c.get("kea_rk",0)
        sm["kea_tot"]      += c.get("kea_tot",0)

LABSM = {"total_intake":"Total Intake","total_kea":"Total KEA (100%)",
         "kea_ph":"PH 5%","kea_spl":"SPL","kea_hk":"HK","kea_rk":"RK","kea_tot":"TOT HK-RK"}
print(f"\n{SEP}")
print("  ANNEXURE M VERIFICATION vs PDF Grand Total")
print(SEP)
all_ok_m = True
for k,label in LABSM.items():
    pv=PDF_M[k]; ov=sm[k]; diff=ov-pv
    ok="OK" if diff==0 else f"OFF {diff:+d}"
    if diff!=0: all_ok_m=False
    print(f"  {label:<22} {pv:>8} {ov:>8} {diff:>+8}  {ok}{'  <---' if diff!=0 else ''}")
print(SEP)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok_m else 'MISMATCHES - need tuning'}")
print(f"  Colleges: {len(colleges_m)}/1")
