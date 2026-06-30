import pdfplumber
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

def clean_name(name):
    n = name.lower()
    n = n.replace('&', 'and')
    n = re.sub(r'\bengg\b', 'engineering', n)
    n = re.sub(r'\btech\b', 'technology', n)
    n = re.sub(r'\bcoll\b', 'college', n)
    n = re.sub(r'\binst\b', 'institute', n)
    n = re.sub(r'\buniv\b', 'university', n)
    n = re.sub(r'\bsch\b', 'school', n)
    n = re.sub(r'\bdept\b', 'department', n)
    n = re.sub(r'[^a-z0-9]', '', n)
    return n

def clean_course_name(name):
    n = name.lower()
    n = n.replace("sicence", "science")
    # Strip common prefixes like B.Tech in, B Tech in, BTech in, B Tech, B.Tech, B.Technology in
    n = re.sub(r'^b\s*(\.?)\s*(tech|technology)\s+(in\s+)?', '', n)
    n = n.replace('&', 'and')
    n = re.sub(r'\bengg\b', 'engineering', n)
    n = re.sub(r'\btech\b', 'technology', n)
    n = re.sub(r'[^a-z0-9]', '', n)
    return n

CLEAN_SHORT_CODE_MAP = {
    "cs": "computerscienceandengineering",
    "is": "informationscienceandengineering",
    "ec": "electronicsandcommunicationengineering",
    "ee": "electricalandelectronicsengineering",
    "me": "mechanicalengineering",
    "ce": "civilengineering",
    "bt": "biotechnology",
    "ch": "chemicalengineering",
    "ai": "artificialintelligenceandmachinelearning",
    "am": "artificialintelligenceandmachinelearning",
    "aiml": "computerscienceandengineeringartificialintelligenceandmachinelearning",
    "cam": "computerscienceandengineeringartificialintelligenceandmachinelearning",
    "ds": "computerscienceandengineeringdatascience",
    "ad": "artificialintelligenceanddatascience",
    "cads": "artificialintelligenceanddatascience",
    "ci": "computerscienceandengineeringinternetofthingsandcybersecurityincludingblockchaintechnology",
    "ro": "roboticsandautomation",
    "re": "roboticsengineering",
    "vlsi": "vlsidesignandtechnology",
    "ev": "vlsidesignandtechnology",
    "es": "embeddedsystemsandvlsi"
}

def courses_are_compatible(name1, name2):
    n1 = clean_course_name(name1)
    n2 = clean_course_name(name2)
    c1 = CLEAN_SHORT_CODE_MAP.get(n1, n1)
    c2 = CLEAN_SHORT_CODE_MAP.get(n2, n2)
    
    if c1 == c2:
        return True
        
    aiml_variants = {"artificialintelligenceandmachinelearning", "computerscienceandengineeringartificialintelligenceandmachinelearning"}
    if c1 in aiml_variants and c2 in aiml_variants:
        return True
        
    aids_variants = {"artificialintelligenceanddatascience", "computerscienceandengineeringartificialintelligenceanddatascience"}
    if c1 in aids_variants and c2 in aids_variants:
        return True
        
    robotics_variants = {"roboticsandautomation", "computerscienceandengineeringrobotics", "roboticsengineering"}
    if c1 in robotics_variants and c2 in robotics_variants:
        return True
        
    vlsi_variants = {"vlsidesignandtechnology", "embeddedsystemsandvlsi", "electronicsandcommunicationengineeringvlsidesignandtechnology", "embeddedsystemandvlsi"}
    if c1 in vlsi_variants and c2 in vlsi_variants:
        return True
        
    datascience_variants = {"datascience", "datasciences", "computerscienceandengineeringdatascience"}
    if c1 in datascience_variants and c2 in datascience_variants:
        return True
        
    iot_variants = {
        "computerscienceandengineeringinternetofthings",
        "computerscienceandengineeringiotandblockchain",
        "computerscienceandengineeringiotincludingblockchain",
        "computerscienceandengineeringiot",
        "computerscienceandengineeringinternetofthingsandcybersecurityincludingblockchaintechnology",
        "computerscienceandengineeringinternetofthingsandcybersecurityincludingblockchain"
    }
    if c1 in iot_variants and c2 in iot_variants:
        return True
        
    ele_veh_variants = {
        "electricalengineeringelectricalvehicletechnology",
        "electricalengineeringelectricvehicletechnology",
        "electricalandelectronicsengineeringelectricalvehicletechnology",
        "electricalandelectronicsengineeringelectricvehicletechnology"
    }
    if c1 in ele_veh_variants and c2 in ele_veh_variants:
        return True
        
    return False

def load_db():
    with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_std_map():
    with open("course_standardization_map.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_std_map(std_map):
    with open("course_standardization_map.json", "w", encoding="utf-8") as f:
        json.dump(std_map, f, indent=2, ensure_ascii=False)

def standardize_name(course_name, std_map):
    c_clean = course_name.strip().upper()
    if c_clean in std_map:
        return std_map[c_clean]
    
    norm = course_name.strip()
    norm = re.sub(r'\bENGG\b', 'Engineering', norm, flags=re.IGNORECASE)
    norm = re.sub(r'\bTECH\b', 'Technology', norm, flags=re.IGNORECASE)
    norm = norm.replace('&', 'and')
    norm = re.sub(r'\s+', ' ', norm).strip()
    
    for k, v in std_map.items():
        if norm.upper() == k.upper() or norm.upper() == v.upper():
            std_map[c_clean] = v
            return v
            
    title_name = norm.title()
    for w in ["And", "Of", "In", "With", "To"]:
        title_name = re.sub(rf'\b{w}\b', w.lower(), title_name)
    title_name = title_name.replace("Cse", "CSE").replace("Ece", "ECE").replace("Ise", "ISE").replace("Eee", "EEE").replace("Vlsi", "VLSI").replace("Aiml", "AIML").replace("Iot", "IoT").replace("Ai", "AI")
    
    std_map[c_clean] = title_name
    print(f"Registering new course standardization: '{course_name}' -> '{title_name}'")
    return title_name

COLLEGE_ALIASES = {
    clean_name("K L E Technological Univeristy, Belgaum Campus (Formerly KLE Dr M.S.Sheshgiri College of Engineering and Technology)"): "K L E Technological University, Belgaum Campus",
    clean_name("SAPTHAGIRI NPS UNIVERISTY"): "SAPTHAGIRI NPS UNIVERSITY",
    clean_name("Univesity of Visvesvaraya College of Engineering (A State Autonomous Public University on IIT Model)"): "University of Visvesvaraya College of Engineering (A State Autonomous Public University on IIT Model)",
    clean_name("Adhichunchanagiri University (Formerly B G S Institute of Technology)"): "Adhichunchanagiri University (Formerly B G S Institute of Technology, BG Nagara)",
    clean_name("School of Planning and Architchure, University of Mysore"): "School of Planning and Architchure, University of Mysore",
    clean_name("A J Institute Of Engineering And Technology.Kottar chowki Boloor Village Mangalore"): "A J Institute Of Engineering And Technology, Mangalore",
}

def parse_special_seats():
    db = load_db()
    std_map = load_std_map()
    
    # Reset all special seats fields to ensure clean merge
    for col in db["colleges"]:
        for c in col.get("courses", []):
            for k in ["sports", "ncc", "sct_guides", "defence", "k_defence", "ex_defence", "capf", "ai", "xcapf", "tot_special_seats"]:
                if k in c:
                    del c[k]
                    
    # Map standard colleges (exclude E/V)
    aided_map = {}
    standard_map = {}
    revised_map = {}
    for col in db["colleges"]:
        c_clean = clean_name(col["college_name"])
        if col["annexure"] in ("E", "V"):
            revised_map[c_clean] = col
            continue
        if col["annexure"] == "B":
            aided_map[c_clean] = col
        else:
            standard_map[c_clean] = col
        
    parsed_count = 0
    merged_count = 0
    unmatched_colleges = set()
    unmatched_courses = []
    
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        # Pages 362 to 428 (Index 361 to 427)
        for pg_num in range(362, 429):
            page = pdf.pages[pg_num - 1]
            tables = page.find_tables()
            
            # Sort tables by top coordinate
            tables = sorted(tables, key=lambda t: t.bbox[1])
            
            previous_bottom = 0
            for t in tables:
                bbox = t.bbox
                
                # Extract text above the table
                crop = page.crop((0, previous_bottom, page.width, bbox[1]))
                text_above = crop.extract_text() or ""
                
                # Determine college name from lines above table
                lines_above = [l.strip() for l in text_above.splitlines() if l.strip()]
                clean_lines = []
                for l in lines_above:
                    # Ignore header elements and footer elements
                    if re.match(r'^(PAGE \d+|\d+/\d+/\d+|ENGINEERING SPECIAL)', l, re.IGNORECASE):
                        continue
                    if "annexure total" in l.lower() or "ins total" in l.lower():
                        continue
                    clean_lines.append(l)
                
                if not clean_lines:
                    raw_college_name = ""
                else:
                    raw_college_name = " ".join(clean_lines).strip()
                
                # Match college
                c_clean = clean_name(raw_college_name)
                if c_clean in COLLEGE_ALIASES:
                    c_clean = clean_name(COLLEGE_ALIASES[c_clean])
                    
                active_college = None
                if pg_num in (368, 369, 370):
                    active_college = aided_map.get(c_clean)
                    if not active_college:
                        active_college = standard_map.get(c_clean)
                else:
                    active_college = standard_map.get(c_clean)
                    if not active_college:
                        active_college = aided_map.get(c_clean)
                        
                if not active_college and raw_college_name:
                    # Try substring fuzzy match
                    if pg_num in (368, 369, 370):
                        for k, col in aided_map.items():
                            if c_clean in k or k in c_clean:
                                active_college = col
                                break
                        if not active_college:
                            for k, col in standard_map.items():
                                if c_clean in k or k in c_clean:
                                    active_college = col
                                    break
                    else:
                        for k, col in standard_map.items():
                            if c_clean in k or k in c_clean:
                                active_college = col
                                break
                        if not active_college:
                            for k, col in aided_map.items():
                                if c_clean in k or k in c_clean:
                                    active_college = col
                                    break
                    
                    # Try revised colleges as a fallback
                    if not active_college:
                        active_college = revised_map.get(c_clean)
                        if not active_college:
                            for k, col in revised_map.items():
                                if c_clean in k or k in c_clean:
                                    active_college = col
                                    break
                                    
                    if not active_college:
                        unmatched_colleges.add(raw_college_name)
                
                # Extract cell data
                cells = t.extract()
                if cells and len(cells) > 1:
                    headers = [c.upper() if c else "" for c in cells[0]]
                    if "SPORTS" in headers:
                        # Process course rows
                        for row in cells[1:]:
                            if not row or len(row) < 11:
                                continue
                            
                            # Row course name
                            raw_course = row[0] or ""
                            raw_course = raw_course.replace("\n", " ").strip()
                            
                            # Skip footer rows
                            if re.match(r'^(INS TOTAL|TOTAL|ANNEXURE TOTAL)', raw_course, re.IGNORECASE):
                                continue
                            
                            # Parse seats
                            nums = []
                            for cell in row[1:11]:
                                val = cell or "0"
                                val = val.replace("\n", "").strip()
                                nums.append(int(val) if val.isdigit() else 0)
                                
                            parsed_count += 1
                            
                            if active_college:
                                # Standardize course name
                                std_course = standardize_name(raw_course, std_map)
                                
                                # Match course in college using robust clean_course_name
                                course_entry = None
                                for c in active_college["courses"]:
                                    if clean_course_name(c["course_name"]) == clean_course_name(std_course):
                                        course_entry = c
                                        break
                                
                                if not course_entry:
                                    # Fallback raw match
                                    for c in active_college["courses"]:
                                        if clean_course_name(c["course_name"]) == clean_course_name(raw_course):
                                            course_entry = c
                                            break
                                            
                                if not course_entry:
                                    # Fallback compatible course match
                                    for c in active_college["courses"]:
                                        if courses_are_compatible(c["course_name"], std_course) or courses_are_compatible(c["course_name"], raw_course):
                                            course_entry = c
                                            print(f"  Fuzzy matched special seat '{std_course}' (raw: '{raw_course}') to '{c['course_name']}' in '{active_college['college_name']}'")
                                            break
                                            
                                if not course_entry and ("JAYACHAMARAJENDRA" in active_college["college_name"].upper() or "SJCE" in active_college["college_name"].upper()):
                                    # Try to find JSS University
                                    jss_uni = None
                                    for col_key, col in standard_map.items():
                                        if ("JSS SCIENCE" in col["college_name"].upper() or "JSS UNIVERSITY" in col["college_name"].upper()) and "JAYACHAMARAJENDRA" not in col["college_name"].upper():
                                            jss_uni = col
                                            break
                                    if jss_uni:
                                        # Try to match the course in JSS University
                                        for c in jss_uni["courses"]:
                                            if courses_are_compatible(c["course_name"], std_course) or courses_are_compatible(c["course_name"], raw_course):
                                                course_entry = c
                                                print(f"  Redirecting special seat for '{std_course}' from SJCE to JSS University course '{c['course_name']}'")
                                                break
                                            
                                if course_entry:
                                    course_entry["sports"] = nums[0]
                                    course_entry["ncc"] = nums[1]
                                    course_entry["sct_guides"] = nums[2]
                                    course_entry["defence"] = nums[3]
                                    course_entry["k_defence"] = nums[4]
                                    course_entry["ex_defence"] = nums[5]
                                    course_entry["capf"] = nums[6]
                                    course_entry["ai"] = nums[7]
                                    course_entry["xcapf"] = nums[8]
                                    course_entry["tot_special_seats"] = nums[9]
                                    merged_count += 1
                                else:
                                    unmatched_courses.append((active_college["college_name"], active_college["annexure"], raw_course, std_course, nums))
                
                previous_bottom = bbox[3]
                
    print(f"\nParsing Complete:")
    print(f"  Parsed {parsed_count} course rows from Special Category sheets.")
    print(f"  Successfully merged {merged_count} rows into standard courses.")
    print(f"  Unmatched colleges: {len(unmatched_colleges)}")
    if unmatched_colleges:
        print("  Sample unmatched colleges:")
        for uc in list(unmatched_colleges)[:5]:
            print(f"    - '{uc}' (cleaned: '{clean_name(uc)}')")
            
    print(f"  Unmatched courses: {len(unmatched_courses)}")
    if unmatched_courses:
        print("  Sample unmatched courses:")
        for uc in unmatched_courses[:5]:
            print(f"    - College: '{uc[0]}' (Ann: {uc[1]}), Raw: '{uc[2]}', Standard: '{uc[3]}'")
            
    # For any unmatched course, create a new course entry in the college
    created_courses_count = 0
    for uc in unmatched_courses:
        col_name = uc[0]
        col_ann = uc[1]
        std_course = uc[3]
        nums = uc[4]
        
        # Find college in db by name and annexure
        col = next(c for c in db["colleges"] if c["college_name"] == col_name and c["annexure"] == col_ann)
        new_c = {
            "course_name": std_course,
            "total_intake": 0,
            "total_kea_seats": 0,
            "snq_5pct": 0, "kea_ph": 0, "kea_spl": 0, "kea_hk": 0, "kea_rk": 0, "kea_tot": 0,
            "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 0,
            "sports": nums[0],
            "ncc": nums[1],
            "sct_guides": nums[2],
            "defence": nums[3],
            "k_defence": nums[4],
            "ex_defence": nums[5],
            "capf": nums[6],
            "ai": nums[7],
            "xcapf": nums[8],
            "tot_special_seats": nums[9]
        }
        col["courses"].append(new_c)
        created_courses_count += 1
        
    print(f"  Created {created_courses_count} new course records for courses that only exist for special category seats.")
    
    # Manually Merge Page 429 Special Category Seats (scanned image page)
    print("\nMerging Page 429 Special Category Seats manually...")
    
    # 1. Constituent College of VTU, Chintamani Chikaballapura (Ann: Z)
    # Course: Computer Science and Engineering (Artificial Intelligence and Machine Learning) -> sports = 1, tot_special_seats = 1
    chintamani_z = next((c for c in db["colleges"] if c["college_name"].strip().lower() == "constituent college of vtu, chintamani chikaballapura" and c["annexure"] == "Z"), None)
    if chintamani_z:
        target_clean = clean_course_name("COMPUTER SCIENCE AND ENGINEERING (AIML)")
        course = next((c for c in chintamani_z["courses"] if clean_course_name(c["course_name"]) == target_clean), None)
        if course:
            course["sports"] = course.get("sports", 0) + 1
            course["tot_special_seats"] = course.get("tot_special_seats", 0) + 1
            print("  Merged Chintamani Ann Z: CSE-AIML -> sports + 1")
            
    # 2. University B.D.T College of Engineering, Davanagere (Ann: Z)
    # Courses:
    # - Computer Science and Engineering -> ncc = 1, tot_special_seats = 1
    # - Electronics and Communication Engineering -> sports = 1, tot_special_seats = 1
    # - Mechanical Engineering -> ex_defence = 1, tot_special_seats = 1
    bdt_z = next((c for c in db["colleges"] if c["college_name"].strip().lower() == "university b.d.t college of engineering, davanagere" and c["annexure"] == "Z"), None)
    if bdt_z:
        # CSE
        target_cse = clean_course_name("Computer Science and Engineering")
        cse = next((c for c in bdt_z["courses"] if clean_course_name(c["course_name"]) == target_cse), None)
        if cse:
            cse["ncc"] = cse.get("ncc", 0) + 1
            cse["tot_special_seats"] = cse.get("tot_special_seats", 0) + 1
            print("  Merged BDT Davanagere Ann Z: CSE -> ncc + 1")
        # ECE
        target_ece = clean_course_name("Electronics and Communication Engineering")
        ece = next((c for c in bdt_z["courses"] if clean_course_name(c["course_name"]) == target_ece), None)
        if ece:
            ece["sports"] = ece.get("sports", 0) + 1
            ece["tot_special_seats"] = ece.get("tot_special_seats", 0) + 1
            print("  Merged BDT Davanagere Ann Z: ECE -> sports + 1")
        # Mech
        target_mech = clean_course_name("Mechanical Engineering")
        mech = next((c for c in bdt_z["courses"] if clean_course_name(c["course_name"]) == target_mech), None)
        if mech:
            mech["ex_defence"] = mech.get("ex_defence", 0) + 1
            mech["tot_special_seats"] = mech.get("tot_special_seats", 0) + 1
            print("  Merged BDT Davanagere Ann Z: ME -> ex_defence + 1")
            
    # Rename Sri Venkateshwara College of Engineering to include (AUTONOMOUS)
    renamed_count = 0
    for col in db["colleges"]:
        if "sri venkateshwara college of engineering" in col["college_name"].lower() or "sri venkateswara college of engineering" in col["college_name"].lower():
            col["college_name"] = "Sri Venkateshwara College of Engineering, Bangalore (AUTONOMOUS)"
            renamed_count += 1
    print(f"  Renamed {renamed_count} Sri Venkateshwara College of Engineering entries to include (AUTONOMOUS).")
    
    save_db(db)
    save_std_map(std_map)
    print("Saved updated seat_matrix_data.json and course_standardization_map.json")

if __name__ == "__main__":
    parse_special_seats()
