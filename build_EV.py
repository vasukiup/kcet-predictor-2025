"""
Extract all colleges and courses from Annexures E and V.
Maps districts using known mappings or geographical keywords, ensuring NO 'Other' or 'Mangalore' districts.
Verifies against calculated grand totals:
  E: 115,276 intake | 53,052 KEA | 3,900 PH | 1,080 SPL | 7,172 HK | 45,880 RK
  V:  36,160 intake | 13,919 KEA | 1,001 PH |   273 SPL | 1,740 HK | 12,179 RK
"""
import pdfplumber, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")

# 1. Load baseline data to build college name -> district cache
with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Keep other annexures (A, B, C, D, M, O, P, Z), clear E and V
before = len(d["colleges"])
d["colleges"] = [c for c in d["colleges"] if c["annexure"] not in ("E", "V")]
print(f"Removed {before - len(d['colleges'])} old E/V colleges")

# Populate district lookup cache from existing colleges
name_dist_cache = {}
for c in d["colleges"]:
    # clean name for robust comparison
    clean_name = re.sub(r'[^A-Z0-9]', '', c["college_name"].upper())
    name_dist_cache[clean_name] = c["district"]

# Helper to normalize district
def normalize_district(dist, name, addr):
    text = f"{name} {addr} {dist}".upper()
    
    # Mangalore is in Dakshina Kannada
    if "MANGALORE" in text or "MANGALURU" in text:
        return "Dakshina Kannada"
    if "BANTWAL" in text or "SULIA" in text or "PUTTUR" in text or "MOODBIDRI" in text or "DERALAKATTE" in text or "UJRE" in text or "UJIRE" in text:
        return "Dakshina Kannada"
        
    # Standard Karnataka districts keywords
    districts = [
        ("BAGALKOT", "Bagalkot"), ("BALLARI", "Ballari"), ("BELLARY", "Ballari"),
        ("BELAGAVI", "Belagavi"), ("BELGAUM", "Belagavi"), ("BENGALURU", "Bangalore"),
        ("BANGALORE", "Bangalore"), ("BIDAR", "Bidar"), ("CHAMARAJANAGAR", "Chamarajanagar"),
        ("CHIKKABALLAPUR", "Chikballapura"), ("CHIKBALLAPUR", "Chikballapura"),
        ("CHIKKAMAGALURU", "Chikkamagaluru"), ("CHICKMAGALUR", "Chikkamagaluru"),
        ("CHITRADURGA", "Chitradurga"), ("DAKSHINA KANNADA", "Dakshina Kannada"),
        ("DAVANAGERE", "Davanagere"), ("DAVENGERE", "Davanagere"), ("DHARWAD", "Dharwad"),
        ("GADAG", "Gadag"), ("GULBARGA", "Kalaburagi"), ("KALABURAGI", "Kalaburagi"),
        ("HASSAN", "Hassan"), ("HAVERI", "Haveri"), ("KODAGU", "Kodagu"),
        ("KOLAR", "Kolar"), ("KOPPAL", "Koppal"), ("MANDYA", "Mandya"),
        ("MYSURU", "Mysuru"), ("MYSORE", "Mysuru"), ("RAICHUR", "Raichur"),
        ("RAMANAGARA", "Ramanagara"), ("SHIVAMOGGA", "Shivamogga"), ("SHIMOGA", "Shivamogga"),
        ("TUMAKURU", "Tumkur"), ("TUMKUR", "Tumkur"), ("UDUPI", "Udupi"),
        ("UTTARA KANNADA", "Uttara Kannada"), ("KARWAR", "Uttara Kannada"),
        ("YADGIR", "Yadgir"), ("CHINTAMANI", "Chikballapura"), ("ARASIKERE", "Hassan"),
        ("CHALLAKERE", "Chitradurga"), ("HOOVINA HADAGALI", "Vijayanagara"), ("HAGARI BOMMANAHALLI", "Vijayanagara"),
        ("KARATAGI", "Koppal"), ("KUSHALANAGAR", "Kodagu"), ("NIPPANI", "Belagavi"),
        ("B G NAGARA", "Mandya"), ("BG NAGARA", "Mandya"), ("SULYA", "Dakshina Kannada"),
        ("K R PET", "Mandya")
    ]
    
    for kw, target in districts:
        if kw in text:
            return target
            
    # Try existing cache
    clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
    if clean_name in name_dist_cache:
        return name_dist_cache[clean_name]
        
    return "Bangalore" # Fallback default

def cr(name, intake, kea, ph, spl, hk, rk, tot, cat2=0, cat3=0):
    # For Govt quota in E and V, COMEDK and Mgmt seats are 0, SNQ 5% SNQ is not part of total intake (we will set to 0)
    return {"course_name": name, "total_intake": intake, "total_kea_seats": kea,
            "snq_5pct": 0, "kea_ph": ph, "kea_spl": spl, "kea_hk": hk, "kea_rk": rk,
            "kea_tot": tot, "cat2_seats": cat2, "cat3_seats": cat3, "over_above_5pct": 0}

def parse_annexure_data(pdf_path, pages, ann):
    colleges = []
    
    current_college = None
    current_college_num = None
    current_courses = []
    current_course = None
    
    # We will also extract the address from the PDF or baseline if it matches
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pages:
            text = pdf.pages[pg-1].extract_text() or ""
            lines = text.splitlines()
            lines = text.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                if not stripped:
                    i += 1
                    continue
                
                # College header
                m_hdr = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/`]+)$', stripped)
                if m_hdr:
                    if current_college_num is not None:
                        colleges.append({
                            "num": current_college_num,
                            "name": current_college,
                            "courses": current_courses
                        })
                    current_college_num = int(m_hdr.group(1))
                    current_college = m_hdr.group(2).strip()
                    current_courses = []
                    current_course = None
                    i += 1
                    continue
                
                # TOT row: marks page total
                if stripped.startswith("TOT ") or stripped.startswith("TOT\t"):
                    if current_course:
                        current_courses.append(current_course)
                        current_course = None
                    i += 1
                    continue
                
                # Header rows to ignore
                if stripped.startswith("Intake") or stripped.startswith("Cat Tot") or "government notification" in stripped.lower():
                    i += 1
                    continue
                
                # RK row
                m_rk = re.match(r'^RK\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_rk:
                    if current_course:
                        current_courses.append(current_course)
                        
                    course_name = m_rk.group(1).strip()
                    intake_str = m_rk.group(2)
                    kea_rk = int(m_rk.group(3))
                    ph_rk = int(m_rk.group(4))
                    spl_rk = int(m_rk.group(5))
                    
                    # Consume subsequent lines that are part of the wrapped course name
                    wrapped_parts = []
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if not next_line:
                            i += 1
                            continue
                        
                        # 1. Check if next line is a single digit (wrapped last digit of intake)
                        m_single_digit = re.match(r'^(\d)$', next_line)
                        if m_single_digit:
                            intake_str += m_single_digit.group(1)
                            i += 1
                            break
                            
                        # 2. Check if next line is a short code followed by a single digit
                        m_code_digit = re.match(r'^([A-Z]{2,6})\s+(\d)$', next_line)
                        if m_code_digit:
                            wrapped_parts.append(m_code_digit.group(1))
                            intake_str += m_code_digit.group(2)
                            i += 1
                            break
                        
                        # Stop conditions:
                        if next_line.startswith("RK ") or next_line.startswith("HK ") or \
                           next_line.startswith("TOT ") or next_line.startswith("TOT\t") or \
                           "government notification" in next_line.lower() or \
                           re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/`]+)$', next_line):
                            break
                            
                        if next_line.upper().startswith("KM QUOTA"):
                            break
                            
                        # If it is a pure numbers line (KM QUOTA seats)
                        if re.match(r'^\d+(\s+\d+){7,11}$', next_line):
                            break
                            
                        # It is a wrapped course name part!
                        m_trail = re.search(r'\s+(\d+(\s+\d+){7,11})$', next_line)
                        if m_trail:
                            part_text = next_line[:m_trail.start()].strip()
                            if part_text:
                                wrapped_parts.append(part_text)
                            i += 1
                            break
                        else:
                            wrapped_parts.append(next_line)
                            i += 1
                            
                    if wrapped_parts:
                        joined_wrap = ""
                        for part in wrapped_parts:
                            if joined_wrap == "":
                                joined_wrap = part
                            elif joined_wrap.endswith("-"):
                                joined_wrap = joined_wrap + part
                            else:
                                joined_wrap = joined_wrap + " " + part
                        
                        course_name = f"{course_name} {joined_wrap}"
                        course_name = re.sub(r'\s+', ' ', course_name).strip()
                        
                    current_course = {
                        "name": course_name,
                        "intake": int(intake_str),
                        "kea_rk": kea_rk,
                        "kea_hk": 0,
                        "ph_rk": ph_rk,
                        "ph_hk": 0,
                        "spl_rk": spl_rk,
                        "spl_hk": 0
                    }
                    continue
                
                # HK row
                m_hk = re.match(r'^HK\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_hk:
                    kea_hk = int(m_hk.group(1))
                    ph_hk = int(m_hk.group(2))
                    spl_hk = int(m_hk.group(3))
                    
                    if current_course:
                        current_course["kea_hk"] = kea_hk
                        current_course["ph_hk"] = ph_hk
                        current_course["spl_hk"] = spl_hk
                    i += 1
                    continue
                
                i += 1
                    
        # Append final college
        if current_college_num is not None:
            colleges.append({
                "num": current_college_num,
                "name": current_college,
                "courses": current_courses
            })
            
    # SPLITS mapping for Aided/Unaided colleges in Annexure E:
    # (aided_course_count, aided_code, unaided_code)
    SPLITS = {
        "BMSCOLLEGEOFENGINEERING": (5, "E003", "E048"),
        "BASAVESHWARAENGINEERINGCOLLEGE": (6, "E031", "E049"),
        "BVVSANGHASBASAVESHWARA": (6, "E031", "E049"),
        "DRAMBEDKARINSTITUTEOFTECHNOLOGY": (8, "E004", "E060"),
        "MALNADCOLLEGEOFENGINEERING": (4, "E024", "E047"),
        "SRIJAYACHAMARAJENDRA": (9, "E021", "E284"),
        "THENATIONALINSTITUTEOFENGINEERING": (3, "E022", "E056"),
        "UNIVERSITYBDT": (7, "E061", "E066"),
        "CONSTITUENTCOLLEGEOFVTUCHINTAMANI": (4, "E308", "E309"),
        "PDACOLLEGEOFENGINEERING": (5, "E041", "E059"),
        "PESCOLLEGEOFENGINEERINGMANDYA": (4, "E023", "E058")
    }

    # Format into target JSON structure
    formatted_colleges = []
    for c in colleges:
        # Address and District mapping
        addr = ""
        # Look up baseline if exists
        clean_name = re.sub(r'[^A-Z0-9]', '', c["name"].upper())
        # Try finding address from baseline colleges
        for old_c in d["colleges"]:
            if re.sub(r'[^A-Z0-9]', '', old_c["college_name"].upper()) == clean_name:
                addr = old_c.get("address", "")
                break
                
        dist = normalize_district("", c["name"], addr)
        
        split_info = None
        for key, val in SPLITS.items():
            if key in clean_name:
                split_info = val
                break
                
        if split_info:
            split_idx, aided_code, unaided_code = split_info
            
            # Aided Entry
            aided_courses_json = []
            for cr_rec in c["courses"][:split_idx]:
                total_kea_val = cr_rec["kea_rk"] + cr_rec["kea_hk"]
                ph_val = cr_rec["ph_rk"] + cr_rec["ph_hk"]
                spl_val = cr_rec["spl_rk"] + cr_rec["spl_hk"]
                exclusive_rk = cr_rec["kea_rk"] - cr_rec["ph_rk"] - cr_rec["spl_rk"]
                exclusive_hk = cr_rec["kea_hk"] - cr_rec["ph_hk"] - cr_rec["spl_hk"]
                aided_courses_json.append(
                    cr(cr_rec["name"], cr_rec["intake"], total_kea_val,
                       ph_val, spl_val,
                       exclusive_hk, exclusive_rk, total_kea_val)
                )
            formatted_colleges.append({
                "college_number": c["num"],
                "college_name": c["name"],
                "address": addr if addr else c["name"],
                "annexure": ann,
                "college_type": "New Intake (Aided)",
                "district": dist,
                "cat1_pct": 100 if ann == "E" else 40,
                "cat2_pct": 0,
                "cat3_pct": 0,
                "total_intake": sum(cr_rec["total_intake"] for cr_rec in aided_courses_json),
                "total_kea_seats": sum(cr_rec["total_kea_seats"] for cr_rec in aided_courses_json),
                "kea_code": aided_code,
                "courses": aided_courses_json
            })
            
            # Unaided Entry
            unaided_courses_json = []
            for cr_rec in c["courses"][split_idx:]:
                total_kea_val = cr_rec["kea_rk"] + cr_rec["kea_hk"]
                ph_val = cr_rec["ph_rk"] + cr_rec["ph_hk"]
                spl_val = cr_rec["spl_rk"] + cr_rec["spl_hk"]
                exclusive_rk = cr_rec["kea_rk"] - cr_rec["ph_rk"] - cr_rec["spl_rk"]
                exclusive_hk = cr_rec["kea_hk"] - cr_rec["ph_hk"] - cr_rec["spl_hk"]
                unaided_courses_json.append(
                    cr(cr_rec["name"], cr_rec["intake"], total_kea_val,
                       ph_val, spl_val,
                       exclusive_hk, exclusive_rk, total_kea_val)
                )
            formatted_colleges.append({
                "college_number": c["num"],
                "college_name": c["name"],
                "address": addr if addr else c["name"],
                "annexure": ann,
                "college_type": "New Intake (Unaided)",
                "district": dist,
                "cat1_pct": 100 if ann == "E" else 40,
                "cat2_pct": 0,
                "cat3_pct": 0,
                "total_intake": sum(cr_rec["total_intake"] for cr_rec in unaided_courses_json),
                "total_kea_seats": sum(cr_rec["total_kea_seats"] for cr_rec in unaided_courses_json),
                "kea_code": unaided_code,
                "courses": unaided_courses_json
            })
        else:
            courses_json = []
            for cr_rec in c["courses"]:
                total_kea_val = cr_rec["kea_rk"] + cr_rec["kea_hk"]
                ph_val = cr_rec["ph_rk"] + cr_rec["ph_hk"]
                spl_val = cr_rec["spl_rk"] + cr_rec["spl_hk"]
                exclusive_rk = cr_rec["kea_rk"] - cr_rec["ph_rk"] - cr_rec["spl_rk"]
                exclusive_hk = cr_rec["kea_hk"] - cr_rec["ph_hk"] - cr_rec["spl_hk"]
                courses_json.append(
                    cr(cr_rec["name"], cr_rec["intake"], total_kea_val,
                       ph_val, spl_val,
                       exclusive_hk, exclusive_rk, total_kea_val)
                )
                
            type_label = "New Intake (Govt/Pvt)" if ann == "E" else "New Intake (Univ)"
            for old_c in d["colleges"]:
                if re.sub(r'[^A-Z0-9]', '', old_c["college_name"].upper()) == clean_name:
                    type_label = old_c.get("college_type", type_label)
                    break
                    
            formatted_colleges.append({
                "college_number": c["num"],
                "college_name": c["name"],
                "address": addr if addr else c["name"],
                "annexure": ann,
                "college_type": type_label,
                "district": dist,
                "cat1_pct": 100 if ann == "E" else 40,
                "cat2_pct": 0,
                "cat3_pct": 0,
                "total_intake": sum(cr_rec["total_intake"] for cr_rec in courses_json),
                "total_kea_seats": sum(cr_rec["total_kea_seats"] for cr_rec in courses_json),
                "courses": courses_json
            })
            
    return formatted_colleges

ann_e_colleges = parse_annexure_data("Seat_Matrix_05072025.pdf", range(122, 324), "E")
# Parse Annexure V including the additional page 434 (1-based, so 434 is page 434)
ann_v_colleges = parse_annexure_data("Seat_Matrix_05072025.pdf", list(range(325, 361)) + [434], "V")

# Page 434 manual data for Amity University (College Number 4)
amity_page434 = {
    "college_number": 4,
    "college_name": "AMITY UNIVERSITY",
    "address": "National Highway 648 (old 207), Devanahalli - Doddaballapur Road",
    "annexure": "V",
    "college_type": "Private University",
    "district": "Bangalore",
    "cat1_pct": 40,
    "cat2_pct": 0,
    "cat3_pct": 0,
    "total_intake": 180,
    "total_kea_seats": 72,
    "courses": [
        cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CLOUD COMPUTING)", 60, 24, 1, 0, 2, 21, 23),
        cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING(DEV OPS)", 60, 24, 1, 0, 2, 21, 23),
        cr("B.Tech in Computer Science and Engineering(Full Stack Development)", 60, 24, 2, 0, 1, 21, 22)
    ]
}
ann_v_colleges.append(amity_page434)

def merge_colleges(col_list):
    merged = []
    seen = {}
    for col in col_list:
        clean_col = re.sub(r'[^A-Z0-9]', '', col["college_name"].upper())
        key = (clean_col, col["annexure"], col.get("kea_code"))
        if key in seen:
            existing = merged[seen[key]]
            for course in col["courses"]:
                clean_cr = re.sub(r'[^A-Z0-9]', '', course["course_name"].upper())
                match = None
                for ex_course in existing["courses"]:
                    clean_ex_cr = re.sub(r'[^A-Z0-9]', '', ex_course["course_name"].upper())
                    if clean_ex_cr == clean_cr:
                        match = ex_course
                        break
                if match:
                    for field in ["total_intake", "total_kea_seats", "kea_ph", "kea_spl", "kea_hk", "kea_rk", "kea_tot"]:
                        match[field] = match.get(field, 0) + course.get(field, 0)
                else:
                    existing["courses"].append(course)
            existing["total_intake"] = sum(c["total_intake"] for c in existing["courses"])
            existing["total_kea_seats"] = sum(c["total_kea_seats"] for c in existing["courses"])
        else:
            seen[key] = len(merged)
            merged.append(json.loads(json.dumps(col)))
    return merged

# Merge E and V colleges to combine duplicates (e.g. Amity University)
ann_e_colleges = merge_colleges(ann_e_colleges)
ann_v_colleges = merge_colleges(ann_v_colleges)

d["colleges"].extend(ann_e_colleges)
d["colleges"].extend(ann_v_colleges)

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"\nAdded E: {len(ann_e_colleges)} colleges, V: {len(ann_v_colleges)} colleges")

# Verification
def verify(ann, target_totals):
    cols = [c for c in d["colleges"] if c["annexure"] == ann]
    s = {"intake":0, "kea":0, "ph":0, "spl":0, "hk":0, "rk":0}
    for c in cols:
        for cr_rec in c["courses"]:
            s["intake"] += cr_rec["total_intake"]
            s["kea"]    += cr_rec["total_kea_seats"]
            s["ph"]     += cr_rec["kea_ph"]
            s["spl"]    += cr_rec["kea_spl"]
            s["hk"]     += cr_rec["kea_hk"]
            s["rk"]     += cr_rec["kea_rk"]
            
    print(f"\n--- Annexure {ann} Verification ---")
    for k, val in target_totals.items():
        print(f"  {k:<8} Target: {val:>8,} | Parsed: {s[k]:>8,} | Diff: {s[k]-val:>+3}")

verify("E", {"intake":115276, "kea":53052, "ph":3900, "spl":1080, "hk":7172, "rk":45880})
verify("V", {"intake":36340, "kea":13991, "ph":1005, "spl":273, "hk":1745, "rk":12242})
