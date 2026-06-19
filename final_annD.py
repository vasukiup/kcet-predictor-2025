"""
Final Annexure D rebuild — using exact course data from PDF pages 94-101.
All 16 colleges rebuilt from scratch using confirmed PDF values.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

d["colleges"] = [c for c in d["colleges"] if c["annexure"] != "D"]

def cr(name, intake, kea, ph, spl, hk, rk, tot, cat2, cat3, over):
    return {"course_name":name,"total_intake":intake,"total_kea_seats":kea,
            "snq_5pct":over,"kea_ph":ph,"kea_spl":spl,"kea_hk":hk,"kea_rk":rk,
            "kea_tot":tot,"cat2_seats":cat2,"cat3_seats":cat3,"over_above_5pct":over}

def col(num, name, addr, dist, courses):
    return {"college_number":num,"college_name":name,"address":addr,"annexure":"D",
            "college_type":"Private Unaided Minority Colleges","district":dist,
            "cat1_pct":40,"cat2_pct":30,"cat3_pct":30,
            "total_intake":sum(c["total_intake"] for c in courses),
            "total_kea_seats":sum(c["total_kea_seats"] for c in courses),
            "courses":courses}

ann_d = [
  # ─── PAGE 94 ─────────────────────────────────────────────────────────────
  col(1,"A J Institute Of Engineering And Technology, Kottar chowki Boloor Village Mangalore",
      "KOTTARA CHOWKI BOLOOR VILLAGE, DAKSHINA KANNADA","Dakshina Kannada",[
    cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",           60, 24,1,0, 2,21,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,2),
    cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",120,48,3,1, 3,41,44,36,36,6),
    cr("COMPUTER SCIENCE AND ENGG (IoT & CYBER SEC BLOCKCHAIN)",60,24,1,0,2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  150, 60,3,1, 4,52,56,45,45,7),
    cr("ELECTRONICS ENGINEERING (VLSI DESIGN & TECHNOLOGY)", 60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                180, 72,4,1, 5,62,67,54,54,9),
    cr("INFORMATION SCIENCE AND ENGINEERING",                60, 24,1,0, 2,21,23,18,18,3),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
  ]),
  col(2,"Anjuman Institute of Technology & Management, Bhatkal",
      "ANJUMANABAD, BHATKAL, (U K DIST), PIN 581320","Uttara Kannada",[
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,1),
    cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",120,48,2,1, 3,42,45,36,36,6),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  120, 48,2,1, 3,42,45,36,36,6),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",    60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               30, 12,1,0, 1,10,11, 9, 9,1),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                 60, 24,1,0, 2,21,23,18,18,3),
    cr("MECHANICAL ENGINEERING",                             30, 12,1,0, 1,10,11, 9, 9,2),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",               60, 24,1,0, 2,21,23,18,18,3),
  ]),
  # ─── PAGE 95 ─────────────────────────────────────────────────────────────
  col(3,"Bahubali College of Engineering, Shravanabelagola, Hassan",
      "GOMMATANAGARA, SHRAVANABELAGOLA - 573135 HASSAN","Hassan",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,1, 2,20,22,18,18,3),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,1),
    cr("COMPUTER SCIENCE AND ENGINEERING",                   60, 24,1,1, 1,21,22,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                 60, 24,1,0, 2,21,23,18,18,3),
    cr("INFORMATION SCIENCE AND ENGINEERING",                60, 24,1,1, 2,20,22,18,18,3),
    cr("MECHANICAL ENGINEERING",                             30, 12,1,0, 1,10,11, 9, 9,2),
  ]),
  col(4,"Beary's Institute of Technology, Boliar Village, Bantwal Tq, Mangalore",
      "LANDS END, INNOLI, BOLIYAR VILLAGE, NEAR MANGALORE UNIVERSITY, MANGALORE-574153","Dakshina Kannada",[
    cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",           60, 24,1,0, 2,21,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,1),
    cr("COMPUTER SCIENCE AND ENGG (IoT & CYBER SEC BLOCKCHAIN)",60,24,1,1,1,21,22,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                   60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                 60, 24,2,0, 2,20,22,18,18,3),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
  ]),
  # ─── PAGE 96 ─────────────────────────────────────────────────────────────
  col(5,"Canara Engineering College, Bantwal",
      "BENJANAPADAVU, BANTWAL, PIN 574219, DAKSHINA KANNADA DIST","Dakshina Kannada",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",      120, 48,2,1, 4,41,45,36,36,6),
    cr("COMPUTER SCIENCE AND BUSINESS SYSTEMS",              60, 24,1,0, 2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND DESIGN",                        60, 24,1,0, 2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  180, 72,4,1, 5,62,67,54,54,9),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                120, 48,2,1, 4,41,45,36,36,6),
    cr("INFORMATION SCIENCE AND ENGINEERING",               180, 72,4,1, 5,62,67,54,54,9),
    cr("MECHANICAL ENGINEERING",                             30, 12,1,0, 1,10,11, 9, 9,2),
  ]),
  col(6,"Ghousia Engineering College, Ramanagara",
      "BANGALORE - MYSORE ROAD, RAMANAGARA","Ramanagara",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,0, 2,21,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,1),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  180, 72,4,1, 5,62,67,54,54,9),
    cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",  30, 12,1,0, 1,10,11, 9, 9,2),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               30, 12,1,0, 1,10,11, 9, 9,1),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                 60, 24,1,1, 1,21,22,18,18,3),
    cr("INFORMATION SCIENCE AND ENGINEERING",                60, 24,1,0, 2,21,23,18,18,3),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",               30, 12,0,0, 1,11,12, 9, 9,2),
  ]),
  # ─── PAGE 97 ─────────────────────────────────────────────────────────────
  col(7,"Gurunanak Dev Engineering College, Bidar",
      "MAILOOR ROAD, BIDAR 585403","Bidar",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,0,16, 7,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  60, 24,1,0,16, 7,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",60,24,1,0,16, 7,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGG (IoT & CYBER SEC BLOCKCHAIN)",60,24,1,0,16,7,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  180, 72,4,1,47,20,67,54,54,9),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",    60, 24,2,0,16, 6,22,18,18,3),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               60, 24,1,0,16, 7,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                120, 48,3,1,31,13,44,36,36,6),
    cr("INFORMATION SCIENCE AND ENGINEERING",                60, 24,1,0,16, 7,23,18,18,3),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0,16, 7,23,18,18,3),
  ]),
  col(8,"H.K.B.K. College of Engineering, Bangalore",
      "# 22/1, NAGAWARA, BANGALORE-560045","Bangalore",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",      120, 48,3,1, 3,41,44,36,36,6),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  360,144,7,1,11,125,136,108,108,18),
    cr("ELECTRONICS AND COMMUNICATION ENGG",               180, 72,4,1, 5,62,67,54,54,9),
    cr("INFORMATION SCIENCE AND ENGINEERING",               120, 48,2,1, 4,41,45,36,36,6),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
  ]),
  # ─── PAGE 98 ─────────────────────────────────────────────────────────────
  col(9,"K C T Engineering College, Gulbarga",
      "GULBARGA","Gulbarga",[
    cr("CIVIL ENGINEERING",                                  60, 24,1,0,16, 7,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                   90, 36,2,1,23,10,33,27,27,5),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                 60, 24,1,0,16, 7,23,18,18,3),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0,16, 7,23,18,18,3),
  ]),
  col(10,"M V J College of Engineering, Bangalore (AUTONOMOUS)",
      "NEAR ITPB, CHANNASANDRA, KADUGODI POST, BANGALORE","Bangalore",[
    cr("AERO SPACE ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
    cr("AERONAUTICAL ENGINEERING",                          120, 48,2,1, 3,42,45,36,36,6),
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,0, 2,21,23,18,18,3),
    cr("CHEMICAL ENGINEERING",                               30, 12,1,0, 1,10,11, 9, 9,2),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,2),
    cr("COMPUTER SCIENCE AND DESIGN",                        60, 24,1,0, 2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  240, 96,5,1, 7,83,90,72,72,12),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",    60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               30, 12,1,0, 1,10,11, 9, 9,1),
    cr("ELECTRONICS ENGINEERING (VLSI DESIGN & TECHNOLOGY)", 60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION (ADVANCED COMM TECH)", 60, 24,1,1, 2,20,22,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                180, 72,4,1, 5,62,67,54,54,9),
    cr("INDUSTRIAL IOT",                                     30, 12,0,0, 1,11,12, 9, 9,2),
    cr("INFORMATION SCIENCE AND ENGINEERING",               120, 48,2,1, 3,42,45,36,36,6),
    cr("MECHANICAL ENGINEERING",                             30, 12,1,0, 1,10,11, 9, 9,1),
  ]),
  # ─── PAGE 99 ─────────────────────────────────────────────────────────────
  col(11,"New Horizon College of Engineering, Varthur, Bangalore (AUTONOMOUS)",
      "RING ROAD, NEAR MARATHALLI, BELLANDUR POST, KADUBHISANAHALLI, BANGALORE","Bangalore",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",      180, 72,3,1, 5,63,68,54,54,9),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  480,192,10,1,15,166,181,144,144,24),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",              120, 48,2,1, 4,41,45,36,36,6),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                180, 72,4,1, 5,62,67,54,54,9),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
  ]),
  col(12,"P A College of Engineering, Kairangal, Bantwala Tq, Mangalore",
      "NADUPADAV, NEAR MANGALORE UNIVERSITY, MONTEPADAV POST, KAIRANGALA VILLAGE, BANTWAL-MANGALORE","Dakshina Kannada",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,0, 2,21,23,18,18,3),
    cr("BIO-TECHNOLOGY",                                     30, 12,1,0, 1,10,11, 9, 9,1),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,2),
    cr("COMPUTER SCIENCE AND ENGG (IoT & CYBER SEC BLOCKCHAIN)",60,24,1,0,2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  120, 48,2,1, 3,42,45,36,36,6),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                 60, 24,1,0, 2,21,23,18,18,3),
    cr("MECHANICAL ENGINEERING",                             30, 12,1,0, 1,10,11, 9, 9,1),
  ]),
  # ─── PAGE 100 ────────────────────────────────────────────────────────────
  col(13,"S D M Institute of Tech., Ujire, Dakshina Kannada",
      "UJIRE-574240 DAKSHINA KANNADA KARNATAKA","Dakshina Kannada",[
    cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",           60, 24,1,0, 2,21,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  30, 12,1,0, 1,10,11, 9, 9,1),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  120, 48,2,1, 3,42,45,36,36,6),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               30, 12,1,0, 1,10,11, 9, 9,2),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                120, 48,2,1, 4,41,45,36,36,6),
    cr("INFORMATION SCIENCE AND ENGINEERING",                60, 24,1,0, 2,21,23,18,18,3),
  ]),
  col(14,"SDM College of Engineering, Dharwad (AUTONOMOUS)",
      "DHAVALAGIRI, KALGHATGI ROAD, DHARWAD","Dharwad",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,0, 2,21,23,18,18,3),
    cr("CHEMICAL ENGINEERING",                               30, 12,1,0, 1,10,11, 9, 9,1),
    cr("CIVIL ENGINEERING",                                  90, 36,2,1, 3,30,33,27,27,5),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  120, 48,2,1, 4,41,45,36,36,6),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                120, 48,2,1, 3,42,45,36,36,6),
    cr("INFORMATION SCIENCE AND ENGINEERING",                60, 24,1,0, 2,21,23,18,18,3),
    cr("MECHANICAL ENGINEERING",                            120, 48,3,1, 3,41,44,36,36,6),
  ]),
  # ─── PAGE 101 ────────────────────────────────────────────────────────────
  col(15,"St. Joseph Engineering College, Mangalore (AUTONOMOUS)",
      "MANGALORE","Dakshina Kannada",[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",       60, 24,1,0, 2,21,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  60, 24,1,0, 2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND BUSINESS SYSTEMS",              60, 24,1,0, 2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  240, 96,5,1, 7,83,90,72,72,12),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",    60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               60, 24,1,1, 2,20,22,18,18,3),
    cr("ELECTRONICS ENGINEERING (VLSI DESIGN & TECHNOLOGY)", 60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                120, 48,3,1, 3,41,44,36,36,6),
    cr("MECHANICAL ENGINEERING",                            120, 48,3,1, 3,41,44,36,36,6),
  ]),
  col(16,"The Oxford College of Engineering, Bangalore",
      "HOSUR ROAD, BOMMANAHALLI, BANGALORE","Bangalore",[
    cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",           60, 24,1,0, 2,21,23,18,18,3),
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",      120, 48,3,1, 3,41,44,36,36,6),
    cr("BIO-TECHNOLOGY",                                     60, 24,1,0, 2,21,23,18,18,3),
    cr("CIVIL ENGINEERING",                                  60, 24,1,0, 2,21,23,18,18,3),
    cr("COMPUTER SCIENCE AND ENGINEERING",                  180, 72,4,1, 5,62,67,54,54,9),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",               60, 24,1,0, 2,21,23,18,18,3),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                120, 48,3,1, 3,41,44,36,36,6),
    cr("INFORMATION SCIENCE AND ENGINEERING",               120, 48,2,1, 4,41,45,36,36,6),
    cr("MECHANICAL ENGINEERING",                             60, 24,1,0, 2,21,23,18,18,3),
    cr("MECHATRONICS",                                       60, 24,1,0, 2,21,23,18,18,3),
  ]),
]

d["colleges"].extend(ann_d)

with open("seat_matrix_data.json","w",encoding="utf-8") as f:
    json.dump(d,f,indent=2,ensure_ascii=False)

# ── Verify ────────────────────────────────────────────────────────────────────
PDF_D = {"total_intake":10440,"total_kea":4176,"kea_ph":209,"kea_spl":46,
         "kea_hk":559,"kea_rk":3362,"kea_tot":3921,"cat2":3132,"cat3":3132,"over":522}

colleges_d = [c for c in d["colleges"] if c["annexure"]=="D"]
s = {k:0 for k in PDF_D}
for col_rec in colleges_d:
    for c in col_rec["courses"]:
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

SEP="-"*66
print(SEP)
print("  ANNEXURE D FINAL VERIFICATION vs PDF Grand Total")
print(SEP)
print(f"  {'Field':<22} {'PDF':>8} {'Ours':>8} {'Diff':>8}  Status")
print(SEP)
all_ok=True
for k,label in LABS.items():
    pv=PDF_D[k]; ov=s[k]; diff=ov-pv
    ok="OK" if diff==0 else f"OFF {diff:+d}"
    if diff!=0: all_ok=False
    print(f"  {label:<22} {pv:>8} {ov:>8} {diff:>+8}  {ok}{'  <---' if diff!=0 else ''}")
print(SEP)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'MISMATCHES'}")
print(f"  Colleges: {len(colleges_d)}/16")

# Per-college check
if not all_ok:
    PDF_INS = {1:780,2:510,3:300,4:330,5:750,6:480,7:780,8:840,
               9:270,10:1170,11:1020,12:390,13:420,14:660,15:840,16:900}
    print()
    for c in sorted(colleges_d,key=lambda x:x["college_number"]):
        ours = sum(cr["total_intake"] for cr in c["courses"])
        pdf  = PDF_INS.get(c["college_number"],0)
        diff = ours-pdf
        if diff!=0:
            print(f"  #{c['college_number']:>2} {c['college_name'][:50]:<50} PDF={pdf} Ours={ours} DIFF={diff:+d}")
