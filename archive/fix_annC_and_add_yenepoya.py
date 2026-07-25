import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# ── Helper to create a course record ─────────────────────────────────────────
def cr(name, intake, kea, ph, spl, hk, rk, tot, cat2, cat3, over):
    return {
        "course_name": name,
        "total_intake": intake, "total_kea_seats": kea,
        "snq_5pct": over, "kea_ph": ph, "kea_spl": spl,
        "kea_hk": hk, "kea_rk": rk, "kea_tot": tot,
        "cat2_seats": cat2, "cat3_seats": cat3,
        "over_above_5pct": over
    }

# ── 1. Fix PDA College (#92) ────────────────────────────────────────────────
pda_found = False
for col in d["colleges"]:
    if col["college_number"] == 92 and col["annexure"] == "C":
        pda_found = True
        # Add the two missing courses
        col["courses"].append(cr("ELECTRICAL & ELECTRONICS ENGINEERING", 20, 9, 0, 0, 6, 3, 9, 6, 5, 1))
        col["courses"].append(cr("INDUSTRIAL & PRODUCTION ENGINEERING", 20, 9, 0, 0, 6, 3, 9, 6, 5, 1))
        
        # Sort courses by name or keep order
        col["total_intake"] = sum(c["total_intake"] for c in col["courses"])
        col["total_kea_seats"] = sum(c["total_kea_seats"] for c in col["courses"])
        print(f"Updated PDA College (#92): intake={col['total_intake']}, kea={col['total_kea_seats']}")
        break

if not pda_found:
    print("WARNING: PDA College (#92) not found in Annexure C!")

# ── 2. Fix PES College (#93) ────────────────────────────────────────────────
pes_found = False
for col in d["colleges"]:
    if col["college_number"] == 93 and col["annexure"] == "C":
        pes_found = True
        # Add the missing EEE course
        col["courses"].append(cr("ELECTRICAL & ELECTRONICS ENGINEERING", 20, 9, 1, 0, 1, 7, 8, 6, 5, 1))
        
        col["total_intake"] = sum(c["total_intake"] for c in col["courses"])
        col["total_kea_seats"] = sum(c["total_kea_seats"] for c in col["courses"])
        print(f"Updated PES College (#93): intake={col['total_intake']}, kea={col['total_kea_seats']}")
        break

if not pes_found:
    print("WARNING: PES College (#93) not found in Annexure C!")

# ── 3. Fix Sampoorna (#115) ─────────────────────────────────────────────────
samp_found = False
for col in d["colleges"]:
    if col["college_number"] == 115 and col["annexure"] == "C":
        samp_found = True
        # Replace courses completely with the 7 correct ones from PDF
        col["courses"] = [
            cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",                            30, 14, 1, 0, 1, 12, 13, 9, 7, 2),
            cr("CIVIL ENGINEERING",                                                   30, 13, 0, 0, 1, 12, 13, 9, 8, 2),
            cr("COMPUTER SCIENCE AND ENGG (ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING)", 30, 13, 1, 0, 1, 11, 12, 9, 8, 1),
            cr("COMPUTER SCIENCE AND ENGINEERING",                                   90, 41, 2, 1, 3, 35, 38, 27, 22, 4),
            cr("ELECTRICAL & ELECTRONICS ENGINEERING",                                15,  6, 0, 0, 1,  5,  6, 5, 4, 1),
            cr("ELECTRONICS AND COMMUNICATION ENGG",                                  60, 27, 1, 0, 2, 24, 26, 18, 15, 3),
            cr("MECHANICAL ENGINEERING",                                              30, 14, 1, 0, 1, 12, 13, 9, 7, 1),
        ]
        col["total_intake"] = sum(c["total_intake"] for c in col["courses"])
        col["total_kea_seats"] = sum(c["total_kea_seats"] for c in col["courses"])
        print(f"Updated Sampoorna College (#115): intake={col['total_intake']}, kea={col['total_kea_seats']}")
        break

if not samp_found:
    print("WARNING: Sampoorna College (#115) not found in Annexure C!")

# ── 4. Add Yenepoya (#147) ──────────────────────────────────────────────────
# Remove college #147 if it was already added to prevent duplicates
d["colleges"] = [col for col in d["colleges"] if not (col["college_number"] == 147 and col["annexure"] == "C")]

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
        cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",                    60, 27, 1, 0, 2, 24, 26, 18, 15, 3),
        cr("COMPUTER SCIENCE AND ENGG (IoT & CYBER SECURITY INCLUDING BLOCK CHAIN TECH)",60, 27, 1, 0, 2, 24, 26, 18, 15, 3),
        cr("COMPUTER SCIENCE AND ENGINEERING",                               120, 54, 3, 1, 4, 46, 50, 36, 30, 6),
        cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",                 60, 27, 1, 0, 2, 24, 26, 18, 15, 3),
        cr("ELECTRICAL & ELECTRONICS ENGINEERING",                            30, 13, 1, 0, 1, 11, 12,  9,  8, 1),
        cr("ELECTRONICS AND COMMUNICATION ENGG",                              60, 27, 1, 0, 2, 24, 26, 18, 15, 3),
        cr("INFORMATION SCIENCE AND ENGINEERING",                             60, 27, 2, 1, 2, 22, 24, 18, 15, 3),
        cr("MECHANICAL ENGINEERING",                                          30, 14, 1, 0, 1, 12, 13,  9,  7, 2),
    ]
}
d["colleges"].append(col147)
print(f"Added Yenepoya Institute of Technology (#147) to Annexure C.")

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Saved updated seat_matrix_data.json with Annexure C fixes.")
