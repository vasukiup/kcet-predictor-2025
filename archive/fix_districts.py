"""
Fix districts for all 29 colleges currently labeled 'Other'.
Uses institution name, address, and known Karnataka geography.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Mapping: (annexure, college_number) -> correct district
DISTRICT_FIX = {
    # ── Annexure A ──────────────────────────────────────────────────────────
    # #9  Govt Engg College Kushalnagar — Madapatna, Kushalanagar → Kodagu
    ("A",  9): "Kodagu",
    # #16 Govt Engg College Naragund  — Naragund, Gadag dist
    ("A", 16): "Gadag",
    # #19 University BDT College of Engineering, Davanagere — Hadadi Road, Davengere
    ("A", 19): "Davanagere",
    # #21 VTU Belagavi (Muddenahalli campus, Chikkaballapur)
    ("A", 21): "Chikkaballapura",

    # ── Annexure C ──────────────────────────────────────────────────────────
    # #4  Aditya College of Engineering — Kamakshipura, Sonnenahalli, near Bangalore
    ("C",  4): "Bangalore Rural",
    # #6  Akash Institute of Engineering — Akkupete Village, Kasaba Hobli → Bangalore Rural (Devanahalli taluk)
    ("C",  6): "Bangalore Rural",
    # #7  Akshaya Institute of Technology, Lingapura → Tumkur dist
    ("C",  7): "Tumkur",
    # #18 BNM Institute of Technology — BSK 2nd Stage, Bangalore
    ("C", 18): "Bangalore",
    # #23 Bapuji Institute of Engineering & Technology — Shamnur Road, Davangere
    ("C", 23): "Davanagere",
    # #24 BASAV Engineering School of Technology, Vijayapura
    ("C", 24): "Vijayapura",
    # #26 BGS College of Engineering — Mahalakshmipura, Bangalore
    ("C", 26): "Bangalore",
    # #33 Cambridge Institute of Technology (North Campus) — Devanahalli Taluk → Bangalore Rural
    ("C", 33): "Bangalore Rural",
    # #39 Coorg Institute of Technology, Kunda, Ponnampet — Kodagu dist
    ("C", 39): "Kodagu",
    # #50 G M Institute of Technology — P.B. Road, Davangere
    ("C", 50): "Davanagere",
    # #53 Ghousia Institute of Technology for Women — Hosur Road, DRC Post, Bangalore
    ("C", 53): "Bangalore",
    # #57 Harsha Institute of Technology — Varadanayakana Hally, Nelamangala Taluk → Bangalore Rural
    ("C", 57): "Bangalore Rural",
    # #61 Jain College of Engineering and Research — Foundry Cluster, Belgaum (Belagavi)
    ("C", 61): "Belagavi",
    # #64 Jain Institute of Technology — Avaragere, Davangere
    ("C", 64): "Davanagere",
    # #69 KLS Viswanathrao Deshpande Institute — Dandeli Road, Haliyal → Uttara Kannada
    ("C", 69): "Uttara Kannada",
    # #73 KVG College of Engineering, Sullia — Kurunjibhag → Dakshina Kannada
    ("C", 73): "Dakshina Kannada",
    # #82 Malnad College of Engineering — Salagame Road, Hassan
    ("C", 82): "Hassan",
    # #83 Mangalore Institute of Technology & Engineering — Badaga Mijar → Dakshina Kannada (Moodbidri)
    ("C", 83): "Dakshina Kannada",
    # #91 New Ebenezer Institute of Technology — Hennur Bagalur, Kothnur Post → Bangalore Rural
    ("C", 91): "Bangalore Rural",
    # #105 Rathinam Institute of Technology — Doddakammanahally, Begur Hobli → Bangalore
    ("C",105): "Bangalore",
    # #108 SJC Institute of Technology — BB Road, Chickballapur
    ("C",108): "Chikkaballapura",
    # #120 Shri Madhwa Vadiraja Institute — Vishwothama Nagar → Udupi (Bantakal, Udupi)
    ("C",120): "Udupi",
    # #127 Sri Basaveswara Institute of Technology — BH Road, Tiptur → Tumkur dist
    ("C",127): "Tumkur",
    # #131 Sri Sairam College of Engineering — Sai Leo Nagar, Anekal Taluk → Bangalore Rural
    ("C",131): "Bangalore Rural",
    # #135 Srinivas Institute of Technology — Srinivas Campus, Mangalore → Dakshina Kannada
    ("C",135): "Dakshina Kannada",
}

# Also fix any "Mangalore" districts to "Dakshina Kannada"
CITY_TO_DISTRICT = {
    "mangalore": "Dakshina Kannada",
    "mangaluru": "Dakshina Kannada",
    "bangalore":  "Bangalore",
    "bengaluru":  "Bangalore",
    "mysore":     "Mysuru",
    "mysuru":     "Mysuru",
    "hubli":      "Dharwad",
    "dharwad":    "Dharwad",
    "belgaum":    "Belagavi",
    "belagavi":   "Belagavi",
    "gulbarga":   "Kalaburagi",
    "kalaburagi": "Kalaburagi",
    "bidar":      "Bidar",
    "bellary":    "Ballari",
    "ballari":    "Ballari",
    "shimoga":    "Shivamogga",
    "shivamogga": "Shivamogga",
    "tumkur":     "Tumkur",
    "tumakuru":   "Tumkur",
    "hassan":     "Hassan",
    "davangere":  "Davanagere",
    "davanagere": "Davanagere",
    "mandya":     "Mandya",
    "udupi":      "Udupi",
    "raichur":    "Raichur",
    "bijapur":    "Vijayapura",
    "vijayapura": "Vijayapura",
    "chitradurga":"Chitradurga",
    "chikmagalur":"Chikmagalur",
    "kodagu":     "Kodagu",
    "coorg":      "Kodagu",
    "kolar":      "Kolar",
    "chikkaballapur":"Chikkaballapura",
    "chickballapur": "Chikkaballapura",
    "chikballapur":  "Chikkaballapura",
    "koppal":     "Koppal",
    "gadag":      "Gadag",
    "bagalkot":   "Bagalkot",
    "yadgir":     "Yadgir",
    "chamarajanagar":"Chamarajanagar",
    "haveri":     "Haveri",
    "dandeli":    "Uttara Kannada",
    "haliyal":    "Uttara Kannada",
    "karwar":     "Uttara Kannada",
    "bhatkal":    "Uttara Kannada",
    "sirsi":      "Uttara Kannada",
    "sullia":     "Dakshina Kannada",
    "puttur":     "Dakshina Kannada",
    "bantwal":    "Dakshina Kannada",
    "moodbidri":  "Dakshina Kannada",
    "ujire":      "Dakshina Kannada",
    "tiptur":     "Tumkur",
    "kunigal":    "Tumkur",
    "nelamangala":"Bangalore Rural",
    "devanahalli":"Bangalore Rural",
    "doddaballapur":"Bangalore Rural",
    "anekal":     "Bangalore Rural",
    "ramanagara": "Ramanagara",
    "channapatna":"Ramanagara",
    "hosur":      "Bangalore",
    "yelahanka":  "Bangalore",
    "nagawara":   "Bangalore",
    "koramangala":"Bangalore",
    "bsk":        "Bangalore",
    "hebbal":     "Bangalore",
    "yeshwanthpur":"Bangalore",
    "hubballi":   "Dharwad",
    "hubli":      "Dharwad",
    "hesaraghatta":"Bangalore",
    "prasannahalli":"Bangalore",
    "kothnur":     "Bangalore",
    "begur":       "Bangalore"
}

fixed = 0

# 1. Apply manual fixes
for c in d["colleges"]:
    key = (c["annexure"], c["college_number"])
    if key in DISTRICT_FIX:
        old = c.get("district","")
        c["district"] = DISTRICT_FIX[key]
        print(f"  FIXED [{c['annexure']}-{c['college_number']:>3}] {c['college_name'][:45]:<45} {old!r} -> {c['district']!r}")
        fixed += 1

# 2. Fix any remaining "Mangalore" typed as district
for c in d["colleges"]:
    dist = c.get("district","")
    if dist.lower() in ("mangalore","mangaluru"):
        c["district"] = "Dakshina Kannada"
        print(f"  RENAMED [{c['annexure']}-{c['college_number']:>3}] {c['college_name'][:45]:<45} 'Mangalore' -> 'Dakshina Kannada'")
        fixed += 1

# 3. Try address-based lookup for any remaining "Other" / empty
still_other = [c for c in d["colleges"] if not c.get("district") or c["district"] in ("Other","other","")]
for c in still_other:
    addr_lower = (c.get("address","") + " " + c.get("college_name","")).lower()
    matched = None
    for keyword, district in CITY_TO_DISTRICT.items():
        if keyword in addr_lower:
            matched = district
            break
    if matched:
        old = c.get("district","")
        c["district"] = matched
        print(f"  AUTO   [{c['annexure']}-{c['college_number']:>3}] {c['college_name'][:45]:<45} -> {matched!r}")
        fixed += 1

# 4. Check remaining
remaining = [c for c in d["colleges"] if not c.get("district") or c["district"] in ("Other","other","")]
print(f"\nFixed: {fixed} colleges")
print(f"Still 'Other'/missing: {len(remaining)}")
for c in remaining:
    print(f"  [{c['annexure']}-{c['college_number']:>3}] {c['college_name'][:60]}  |  {c.get('address','')[:60]}")

with open("seat_matrix_data.json","w",encoding="utf-8") as f:
    json.dump(d,f,indent=2,ensure_ascii=False)
print("\nSaved seat_matrix_data.json")
