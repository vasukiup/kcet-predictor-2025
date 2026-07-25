"""
Annexure C fixes:
1. Add missing college #147 (Yenepoya Institute Of Technology, Mangalore)
2. Fix column mapping for all Annexure C colleges (same shift bug as A/B)
3. Verify against PDF grand total:
   TOTAL: Annexure-C = 95236 | 42856 | 2143 | 460 | 4800 | 35453 | 40253 | 28571 | 23809 | 4762

Annexure C column layout (Private unaided):
  Total Intake | Total KEA (45%) | PH 5% | SPL | HK | RK | TOT HK-RK | CAT-2 COMEDK 30% | CAT-3 MGMT 25% | Over SNQ 5%

College #147 data from image (page 93):
  Name: Yenepoya Institute Of Technology, Mangalore
  Address: VIDYANAGAR N.H 13THODAR MIJAR POST MOODBIDRI MANGALORE TQ
  Courses (CAT-1=45%, CAT-2=30%, CAT-3=25%):
  1 ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING   60  27  1  0  2  24  26  18  15  3
  2 COMPUTER SCIENCE AND ENGG (IoT & CYBER SECURITY INCLUDING BLOCK CHAIN TECH) 60 27 1 0 2 24 26 18 15 3
  3 COMPUTER SCIENCE AND ENGINEERING              120  54  3  1  4  46  50  36  30  6
  4 COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE) 60 27 1 0 2 24 26 18 15 3
  5 ELECTRICAL & ELECTRONICS ENGINEERING           30  13  1  0  1  11  12   9   8  1 (note: Over=1 not 2 based on 5%)
  6 ELECTRONICS AND COMMUNICATION ENGG             60  27  1  0  2  24  26  18  15  3
  7 INFORMATION SCIENCE AND ENGINEERING            60  27  2  1  2  22  24  18  15  3
  8 MECHANICAL ENGINEERING                         30  14  1  0  1  12  13   9   7  2
  Ins Total: 480 216 11 2 16 187 203 144 120 24
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# ── Step 1: Fix column mapping for ALL Annexure C colleges ──────────────────
# Annexure C stores: snq=PH, ph=SPL, spl=HK, hk=RK, rk=TOT, tot=CAT2, cat2=CAT3
# Same shift as A/B, but C also has cat2 and cat3.
# After column fix A/B, we see our extractor already reads:
#   nums[0]=intake, nums[1]=kea, nums[2]=ph, nums[3]=spl,
#   nums[4]=hk, nums[5]=rk, nums[6]=tot, nums[7]=cat2, nums[8]=cat3, nums[9]=over
# But the extractor stored them as snq_5pct, kea_ph, kea_spl, kea_hk, kea_rk, kea_tot, cat2, cat3, over
# So same shift: snq->ph, ph->spl, spl->hk, hk->rk, rk->tot, tot->cat2, cat2->cat3, cat3->over

fixed = 0
for col in d["colleges"]:
    if col["annexure"] != "C":
        continue
    for c in col["courses"]:
        old_snq  = c.get("snq_5pct", 0)
        old_ph   = c.get("kea_ph", 0)
        old_spl  = c.get("kea_spl", 0)
        old_hk   = c.get("kea_hk", 0)
        old_rk   = c.get("kea_rk", 0)
        old_tot  = c.get("kea_tot", 0)
        old_cat2 = c.get("cat2_seats", 0)
        old_cat3 = c.get("cat3_seats", 0)
        old_over = c.get("over_above_5pct", 0)

        c["kea_ph"]          = old_snq
        c["kea_spl"]         = old_ph
        c["kea_hk"]          = old_spl
        c["kea_rk"]          = old_hk
        c["kea_tot"]         = old_rk
        c["cat2_seats"]      = old_tot
        c["cat3_seats"]      = old_cat2
        c["over_above_5pct"] = old_cat3
        c["snq_5pct"]        = old_over
        fixed += 1

print(f"Fixed column mapping for {fixed} course rows in Annexure C")

# ── Step 2: Add College #147 ────────────────────────────────────────────────
def make_c_course(name, intake, kea, ph, spl, hk, rk, tot, cat2, cat3, over):
    return {
        "course_name": name,
        "total_intake": intake, "total_kea_seats": kea,
        "snq_5pct": over, "kea_ph": ph, "kea_spl": spl,
        "kea_hk": hk, "kea_rk": rk, "kea_tot": tot,
        "cat2_seats": cat2, "cat3_seats": cat3,
        "over_above_5pct": over,
    }

col147 = {
    "college_number": 147,
    "college_name": "Yenepoya Institute Of Technology, Mangalore",
    "address": "VIDYANAGAR N.H 13THODAR MIJAR POST MOODBIDRI MANGALORE TQ",
    "annexure": "C",
    "college_type": "Private Unaided Engineering Colleges",
    "district": "Dakshina Kannada",
    "cat1_pct": 45, "cat2_pct": 30, "cat3_pct": 25,
    "total_intake": 480,
    "total_kea_seats": 216,
    "courses": [
        make_c_course("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",                    60,27,1,0,2,24,26,18,15,3),
        make_c_course("COMPUTER SCIENCE AND ENGG (IoT & CYBER SECURITY INCL BLOCKCHAIN",60,27,1,0,2,24,26,18,15,3),
        make_c_course("COMPUTER SCIENCE AND ENGINEERING",                               120,54,3,1,4,46,50,36,30,6),
        make_c_course("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",                 60,27,1,0,2,24,26,18,15,3),
        make_c_course("ELECTRICAL & ELECTRONICS ENGINEERING",                            30,13,1,0,1,11,12, 9, 8,1),
        make_c_course("ELECTRONICS AND COMMUNICATION ENGG",                              60,27,1,0,2,24,26,18,15,3),
        make_c_course("INFORMATION SCIENCE AND ENGINEERING",                             60,27,2,1,2,22,24,18,15,3),
        make_c_course("MECHANICAL ENGINEERING",                                          30,14,1,0,1,12,13, 9, 7,2),
    ],
}
d["colleges"].append(col147)

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"Added college #147: {col147['college_name']}")
print()

# ── Step 3: Verify against PDF grand total ──────────────────────────────────
PDF_TOTAL = {
    "total_intake": 95236,
    "total_kea":    42856,
    "kea_ph":        2143,
    "kea_spl":        460,
    "kea_hk":        4800,
    "kea_rk":       35453,
    "kea_tot":      40253,
    "cat2_seats":   28571,
    "cat3_seats":   23809,
    "over_above":    4762,
}

ann_c = [c for c in d["colleges"] if c["annexure"] == "C"]
sums = {k: 0 for k in PDF_TOTAL}
for col in ann_c:
    for c in col["courses"]:
        sums["total_intake"] += c.get("total_intake", 0)
        sums["total_kea"]    += c.get("total_kea_seats", 0)
        sums["kea_ph"]       += c.get("kea_ph", 0)
        sums["kea_spl"]      += c.get("kea_spl", 0)
        sums["kea_hk"]       += c.get("kea_hk", 0)
        sums["kea_rk"]       += c.get("kea_rk", 0)
        sums["kea_tot"]      += c.get("kea_tot", 0)
        sums["cat2_seats"]   += c.get("cat2_seats", 0)
        sums["cat3_seats"]   += c.get("cat3_seats", 0)
        sums["over_above"]   += c.get("over_above_5pct", 0)

LABELS = {
    "total_intake": "Total Intake",    "total_kea": "Total KEA (45%)",
    "kea_ph":  "PH 5%",               "kea_spl":  "SPL",
    "kea_hk":  "HK",                  "kea_rk":   "RK",
    "kea_tot": "TOT HK-RK",           "cat2_seats":"CAT-2 COMEDK 30%",
    "cat3_seats":"CAT-3 Mgmt 25%",    "over_above":"Over SNQ 5%",
}

SEP = "-" * 66
print(SEP)
print("  ANNEXURE C VERIFICATION vs PDF Grand Total")
print(SEP)
print(f"  {'Field':<22} {'PDF':>9} {'Ours':>9} {'Diff':>8}  Status")
print(SEP)
all_ok = True
for k, label in LABELS.items():
    pv = PDF_TOTAL[k]; ov = sums[k]; diff = ov - pv
    ok = "OK" if diff == 0 else f"OFF {diff:+d}"
    if diff != 0: all_ok = False
    marker = "  <---" if diff != 0 else ""
    print(f"  {label:<22} {pv:>9} {ov:>9} {diff:>+8}  {ok}{marker}")
print(SEP)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'MISMATCHES FOUND'}")
print(f"  Colleges: {len(ann_c)}/147")
