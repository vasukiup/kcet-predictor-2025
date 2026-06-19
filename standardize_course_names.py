import json
import re
import difflib
from collections import Counter

# Dictionary of short codes to keyword matches
SHORT_CODE_MAP = {
    "AD": ["artificial intelligence", "data science"],
    "AE": ["aero"],
    "AG": ["agri"],
    "AI": ["artificial intelligence and machine learning", "artificial intelligence & machine learning"],
    "AM": ["artificial intelligence and machine learning", "artificial intelligence & machine learning"],
    "AS": ["aero"],
    "AT": ["auto", "automobile"],
    "ATMO": ["automobile", "automotive"],
    "BD": ["big data"],
    "BM": ["medical", "bio"],
    "BR": ["biomedical", "robotic"],
    "BT": ["bio", "biotech"],
    "CADS": ["artificial intelligence and data science", "artificial intelligence & data science"],
    "CAI": ["computer science", "artificial intelligence"],
    "CAM": ["artificial intelligence and machine learning", "artificial intelligence & machine learning", "computer science and engineering"],
    "CB": ["business", "system"],
    "CC": ["internet of things", "cyber security", "block chain"],
    "CCS": ["cyber"],
    "CE": ["civil"],
    "CEK": ["civil", "kannada"],
    "CEV": ["environmental"],
    "CG": ["computer science and technology", "computer science & technology"],
    "CH": ["chemical"],
    "CI": ["computer science and design", "computer science & design", "design"],
    "CMP": ["medical"],
    "CO": ["computer science", "iot", "internet of things"],
    "CR": ["ceramics", "cement"],
    "CS": ["computer science and engineering", "computer science & engineering"],
    "CSA": ["computer science", "artificial intelligence"],
    "CSC": ["computer science"],
    "CSD": ["design", "computer science"],
    "CSS": ["computer science and engineering(data science)", "computer science and engineering(dat a science)"],
    "CST": ["computer science", "technology"],
    "CTM": ["construction", "technology", "management"],
    "CY": ["cyber"],
    "DESIGN": ["design"],
    "DG": ["design"],
    "DO": ["devops"],
    "DS": ["data science"],
    "DT": ["data"],
    "EAT": ["advanced", "communication"],
    "EC": ["communication", "telecommunication"],
    "ECS": ["electronics", "computer science"],
    "EE": ["electrical"],
    "EIE": ["instrumentation"],
    "EII": ["industrial", "integrated"],
    "EIT": ["instrumentation"],
    "ELCE": ["electrical", "computer"],
    "EN": ["environmental"],
    "ENV": ["environmental"],
    "EO": ["electronics and computer", "electronics & computer"],
    "ET": ["telecommunication"],
    "EV": ["vlsi"],
    "IAL": ["ial"],
    "IB": ["iot", "blockchain"],
    "IEM": ["management"],
    "IIT": ["industrial", "iot"],
    "IN": ["information science"],
    "IO": ["internet of things", "iot"],
    "IOT": ["iot", "internet of things"],
    "IP": ["production"],
    "IS": ["information science engineering", "information science and engineering"],
    "IT": ["information technology"],
    "IY": ["blockchain"],
    "LC": ["information science and technology", "information science & technology", "technology"],
    "MC": ["computing", "math", "mechatronics"],
    "ME": ["mechanical"],
    "MEE": ["medical", "electronics"],
    "MEK": ["mechanical", "kannada"],
    "MM": ["manufacturing", "mechanical", "smart"],
    "MN": ["mining"],
    "MR": ["marine"],
    "MS": ["mechatronics"],
    "MX": ["mechatronics"],
    "PE": ["petroleum"],
    "PT": ["polymer"],
    "RA": ["robotics", "automation"],
    "RAI": ["robotics", "artificial intelligence"],
    "RE": ["robotic"],
    "RO": ["robotics"],
    "ST": ["silk"],
    "TX": ["textile", "textiles"],
    "UP": ["planning"],
    "VLSI": ["vlsi"]
}

SHORT_CODE_TO_FULL_NAME = {
    "AD": "Artificial Intelligence and Data Science",
    "AE": "Aeronautical Engineering",
    "AG": "Agricultural Engineering",
    "AI": "Artificial Intelligence and Machine Learning",
    "AM": "Artificial Intelligence and Machine Learning",
    "AS": "Aeronautical Engineering",
    "AT": "Automobile Engineering",
    "ATMO": "Automobile Engineering",
    "BD": "Computer Science and Technology (Big Data)",
    "BM": "Bio-Medical Engineering",
    "BR": "Biomedical and Robotic Engineering",
    "BT": "Bio-Technology",
    "CADS": "Artificial Intelligence and Data Science",
    "CAI": "Computer Science and Engineering (Artificial Intelligence)",
    "CAM": "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "CB": "Computer Science and Business Systems",
    "CC": "Computer Science and Engineering (Internet of Things & Cyber Security including Block Chain Technology)",
    "CCS": "Computer Science and Engineering (Cyber Security)",
    "CE": "Civil Engineering",
    "CEK": "Civil Engineering (Kannada Medium)",
    "CEV": "Civil Environmental Engineering",
    "CG": "Computer Science and Technology",
    "CH": "Chemical Engineering",
    "CI": "Computer Science and Design",
    "CMP": "Computer Science and Engineering (Medical Electronics)",
    "CO": "Computer Science and Engineering (Internet of Things)",
    "CR": "Ceramics & Cement Engineering",
    "CS": "Computer Science and Engineering",
    "CSA": "Computer Science and Engineering (Artificial Intelligence)",
    "CSC": "Computer Science",
    "CSD": "Computer Science and Design",
    "CSS": "Computer Science and Engineering (Data Science)",
    "CST": "Computer Science & Technology",
    "CTM": "Construction Technology and Management",
    "CY": "Computer Science and Engineering (Cyber Security)",
    "DESIGN": "Design Engineering",
    "DG": "Design",
    "DO": "Computer Science and Technology (DevOps)",
    "DS": "Computer Science and Engineering (Data Science)",
    "DT": "Data Sciences",
    "EAT": "Electronics and Communication (Advanced Communication Technology)",
    "EC": "Electronics and Communication Engineering",
    "ECS": "Electronics & Computer Science",
    "EE": "Electrical and Electronics Engineering",
    "EIE": "Electronics and Instrumentation Engineering",
    "EII": "Electronics & Communication Engineering (Industrial Integrated)",
    "EIT": "Electronics and Instrumentation Engineering",
    "ELCE": "Electrical & Computer Engineering",
    "EN": "Environmental Engineering",
    "ENV": "Environmental Engineering",
    "EO": "Electronics and Computer Engineering",
    "ET": "Telecommunication Engineering",
    "EV": "VLSI Design and Technology",
    "IAL": "Industrial and Production Engineering",
    "IB": "Computer Science and Engineering (IoT and Blockchain)",
    "IEM": "Industrial Engineering and Management",
    "IIT": "Industrial IoT",
    "IN": "Information Science and Engineering",
    "IO": "Computer Science and Engineering (Internet of Things)",
    "IOT": "Computer Science and Engineering (Internet of Things)",
    "IP": "Industrial and Production Engineering",
    "IS": "Information Science and Engineering",
    "IT": "Information Technology",
    "IY": "Computer Science and Engineering (Blockchain)",
    "LC": "Information Science and Technology",
    "MC": "Mathematics and Computing",
    "ME": "Mechanical Engineering",
    "MEE": "Medical Electronics Engineering",
    "MEK": "Mechanical Engineering (Kannada Medium)",
    "MM": "Mechanical and Smart Manufacturing",
    "MN": "Mining Engineering",
    "MR": "Marine Engineering",
    "MS": "Mechatronics Engineering",
    "MX": "Mechatronics Engineering",
    "PE": "Petroleum Engineering",
    "PT": "Polymer Science and Technology",
    "RA": "Robotics and Automation",
    "RAI": "Robotics and Artificial Intelligence",
    "RE": "Robotics Engineering",
    "RO": "Robotics and Automation",
    "ST": "Silk Technology",
    "TX": "Textiles Technology",
    "UP": "Urban and Regional Planning",
    "VLSI": "VLSI Design and Technology"
}

def expand_short_code(name):
    name_clean = name.strip()
    short_code = None
    m_paren = re.search(r'\(([A-Za-z0-9]{2,6})\)', name_clean)
    if m_paren:
        short_code = m_paren.group(1).upper()
    else:
        m_direct = re.match(r'^([A-Za-z0-9]{2,6})(\s+in)?$', name_clean)
        if m_direct:
            short_code = m_direct.group(1).upper()
            
    if short_code and short_code in SHORT_CODE_TO_FULL_NAME:
        return SHORT_CODE_TO_FULL_NAME[short_code]
    return to_title_case(name)

def super_clean(name):
    n = name.lower()
    n = re.sub(r'^(b\.?\s*tech\s*(in)?|btech\s*(in)?)\s+', '', n)
    n = n.replace('&', 'and')
    n = n.replace('engg', 'engineering')
    n = n.replace('technology', 'tech')
    n = re.sub(r'[^a-z0-9]', '', n)
    n = n.replace('artifical', 'artificial')
    n = n.replace('cpgs', '')
    return n

def clean_typos(name):
    # Remove weird spaces inside common words
    name = re.sub(r'\bDAT\s+A\s+SCIENCE\b', 'DATA SCIENCE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bD\s+ATA\s+SCIENCE\b', 'DATA SCIENCE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCYB\s+ER\s+SECURITY\b', 'CYBER SECURITY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bC\s+YBER\s+SECURITY\b', 'CYBER SECURITY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bBLO\s+CK\s+CHAIN\b', 'BLOCK CHAIN', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTI\s+FICIAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTI\s+FICAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bA\s+RTIFICIAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTIFICAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bUNIVERISTY\b', 'UNIVERSITY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCOMMUNICATION\s+ENGG\b', 'COMMUNICATION ENGINEERING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCOMMUNICATIO\s+N\s+ENGG\b', 'COMMUNICATION ENGINEERING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCOMMUNICATIO\s+N\b', 'COMMUNICATION', name, flags=re.IGNORECASE)
    name = re.sub(r'\bENGG\b', 'ENGINEERING', name, flags=re.IGNORECASE)
    return name

def to_title_case(name):
    # Strip B Tech In prefix
    n = re.sub(r'^(B\s*TECH\s*IN|B\.?\s*TECH\s*IN|BTECH\s*IN)\s+', '', name, flags=re.IGNORECASE)
    n = clean_typos(n)
    
    # Capitalize words correctly, keeping parentheses contents in Title Case too
    words = []
    for word in re.split(r'(\s+|[()&/])', n):
        if not word.strip():
            words.append(word)
            continue
        if word in ['(', ')', '&', '/']:
            words.append(word)
            continue
        # Convert words like "and", "of", "in" to lowercase unless they start the name or follow a parenthesis
        w_lower = word.lower()
        if w_lower in ['and', 'of', 'in', 'including', 'with', 'for'] and len(words) > 0 and not words[-1].endswith('('):
            words.append(w_lower)
        else:
            # Title case
            words.append(word.capitalize())
            
    res = "".join(words).strip()
    return res

def run_standardization():
    print("Loading databases...")
    with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
        sm_data = json.load(f)
        
    with open("round1_cutoffs.json", "r", encoding="utf-8") as f:
        r1 = json.load(f)
    with open("round2_cutoffs.json", "r", encoding="utf-8") as f:
        r2 = json.load(f)
    with open("round3_cutoffs.json", "r", encoding="utf-8") as f:
        r3 = json.load(f)
        
    print("Standardizing course names...")
    
    corrected_colleges = 0
    total_courses_modified = 0
    
    # We will load a fresh baseline to overwrite and clean up name changes
    # so we don't compound previous erroneous runs
    with open("seat_matrix_data_v1_baseline.json", "r", encoding="utf-8") as f:
        baseline_data = json.load(f)
        
    # Copy baseline college list except keep the rebuilt colleges list (since we rebuilt colleges and mapped them)
    # Actually, we can just edit the active seat_matrix_data.json, but wait,
    # did we run build_EV.py just now? Yes! That wrote to seat_matrix_data.json.
    # So we should read from the current active seat_matrix_data.json.
    # But wait! If we run on the active seat_matrix_data.json, will it have names like "Civil Engineering Engineering"?
    # Yes, from the previous run. So we should clean them. Our new to_title_case does not have the "Civil" -> "Civil Engineering" bug,
    # and clean_typos expands "ENGG" -> "ENGINEERING".
    # Let's clean up "Engineering Engineering" -> "Engineering" dynamically!
    
    for col_idx, col in enumerate(sm_data["colleges"]):
        code = col.get("kea_code")
        if not code:
            # Just clean existing names for unmapped colleges
            for c in col["courses"]:
                old_name = c["course_name"]
                new_name = expand_short_code(old_name)
                new_name = new_name.replace("Engineering Engineering", "Engineering")
                if old_name != new_name:
                    c["course_name"] = new_name
                    total_courses_modified += 1
            continue
            
        # Gather all cutoff course names for this college across all rounds in insertion order
        cut_courses = []
        for r_data in [r1, r2, r3]:
            if code in r_data:
                for cc in r_data[code].get("courses", {}).keys():
                    if cc not in cut_courses:
                        cut_courses.append(cc)
                        
        if not cut_courses:
            # No cutoff data found, just clean existing names
            for c in col["courses"]:
                old_name = c["course_name"]
                new_name = expand_short_code(old_name)
                new_name = new_name.replace("Engineering Engineering", "Engineering")
                if old_name != new_name:
                    c["course_name"] = new_name
                    total_courses_modified += 1
            continue
            
        # Match seat matrix courses to cutoff courses
        sm_courses = col["courses"]
        
        mapping = {} # sm_course index -> cutoff course name
        unmapped_sm_indices = list(range(len(sm_courses)))
        available_cut_courses = list(cut_courses)
        
        # 1. Exact clean name matching first (only for unique course names in SM)
        sm_counts = Counter(super_clean(c["course_name"]) for c in sm_courses)
        for idx in list(unmapped_sm_indices):
            sm_c = sm_courses[idx]
            sm_clean = super_clean(sm_c["course_name"])
            
            if sm_counts[sm_clean] > 1:
                continue
                
            exact_matches = [cc for cc in available_cut_courses if super_clean(cc) == sm_clean]
            if len(exact_matches) == 1:
                mapping[idx] = exact_matches[0]
                unmapped_sm_indices.remove(idx)
                available_cut_courses.remove(exact_matches[0])

        # 2. Try prefix clean matching (only for unique course names in SM)
        # E.g. 'COMPUTER SCIENCE AND BUSINESS' starts with / is prefix of 'COMPUTER SCIENCE AND BUSINESS SYSTEMS'
        # and there's only one such match in the cutoff list.
        # 2. Try prefix clean matching (only for unique course names in SM, and NOT for short codes)
        for idx in list(unmapped_sm_indices):
            sm_c = sm_courses[idx]
            name_raw = sm_c["course_name"].strip()
            if re.match(r'^[A-Z]{2,4}$', name_raw, re.IGNORECASE) or name_raw.lower() in ['ce', 'ec', 'ee', 'me', 'cs', 'is', 'bt', 'ch', 'ad', 'ai', 'cb', 'ci', 'ds', 'cy', 'cg', 'ip', 'im', 'iem', 'pt', 'et', 'ev']:
                continue
                
            sm_clean = super_clean(name_raw)
            
            if sm_counts[sm_clean] > 1:
                continue
                
            prefix_matches = []
            for cc in available_cut_courses:
                cc_clean = super_clean(cc)
                if cc_clean.startswith(sm_clean) or sm_clean.startswith(cc_clean):
                    prefix_matches.append(cc)
                    
            if len(prefix_matches) == 1:
                mapping[idx] = prefix_matches[0]
                unmapped_sm_indices.remove(idx)
                available_cut_courses.remove(prefix_matches[0])

        # 3. Match short codes (e.g. CE, EC, (AM), (AS), CS, etc.)
        for idx in list(unmapped_sm_indices):
            sm_c = sm_courses[idx]
            name_clean = sm_c["course_name"].strip()
            short_code = None
            m_paren = re.search(r'\(([A-Z]{2,6})\)', name_clean, re.IGNORECASE)
            if m_paren:
                short_code = m_paren.group(1).upper()
            else:
                m_direct = re.match(r'^([A-Z]{2,6})(\s+in)?$', name_clean, re.IGNORECASE)
                if m_direct:
                    short_code = m_direct.group(1).upper()
                    
            if short_code:
                keywords = SHORT_CODE_MAP.get(short_code, [])
                if keywords:
                    scored = []
                    for cc in available_cut_courses:
                        cc_clean = super_clean(cc)
                        matches = sum(1 for kw in keywords if super_clean(kw) in cc_clean)
                        if matches > 0:
                            scored.append((cc, matches))
                    if scored:
                        scored.sort(key=lambda x: (-x[1], '(' in x[0]))
                        best_cc = scored[0][0]
                        mapping[idx] = best_cc
                        unmapped_sm_indices.remove(idx)
                        available_cut_courses.remove(best_cc)

        # 4. Match remaining duplicates sequentially
        generic_groups = {} # base_clean_name -> list of unmatched sm indices
        for idx in unmapped_sm_indices:
            sm_c = sm_courses[idx]
            sm_clean = super_clean(sm_c["course_name"])
            
            # Clean duplicate course names: e.g. multiple "computer science and engineering"
            # We want to match them to cutoff courses starting with the same clean name
            base = sm_clean
            if len(base) > 12:
                base = base[:12]
            
            matched_group = False
            for g_base in list(generic_groups.keys()):
                if g_base.startswith(base) or base.startswith(g_base):
                    generic_groups[g_base].append(idx)
                    matched_group = True
                    break
            if not matched_group:
                generic_groups[base] = [idx]
                
        for g_base, indices in generic_groups.items():
            if len(indices) == 0:
                continue
            matching_cut_courses = []
            for cc in available_cut_courses:
                cc_clean = super_clean(cc)
                if cc_clean.startswith(g_base) or g_base.startswith(cc_clean[:12]):
                    matching_cut_courses.append(cc)
                    
            if matching_cut_courses:
                indices.sort()
                # Maintain the original insertion order from cut_courses list
                matching_cut_courses.sort(key=lambda x: cut_courses.index(x))
                
                for i, idx in enumerate(indices):
                    if i < len(matching_cut_courses):
                        mapping[idx] = matching_cut_courses[i]
                        unmapped_sm_indices.remove(idx)
                        available_cut_courses.remove(matching_cut_courses[i])
                        
        # 5. Apply standardized course names
        for idx, sm_c in enumerate(sm_courses):
            old_name = sm_c["course_name"]
            if idx in mapping:
                cut_name = mapping[idx]
                new_name = to_title_case(cut_name)
            else:
                new_name = expand_short_code(old_name)
                
            new_name = new_name.replace("Engineering Engineering", "Engineering")
            if old_name != new_name:
                sm_c["course_name"] = new_name
                total_courses_modified += 1
                
        corrected_colleges += 1

    print(f"Standardized course names in {corrected_colleges} colleges.")
    print(f"Total course names modified: {total_courses_modified}")
    
    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(sm_data, f, indent=2, ensure_ascii=False)
    print("Saved standardized seat_matrix_data.json successfully!")

if __name__ == "__main__":
    run_standardization()
