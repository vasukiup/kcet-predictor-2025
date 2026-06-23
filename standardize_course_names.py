import json
import re

# Dictionary of raw course name -> canonical course name
# This contains the direct overrides for specific dirty course names in the seat matrix
MANUAL_OVERRIDE_MAP = {
    "Aero Space Engineering": "Aerospace Engineering",
    "Agriculture Engineering": "Agricultural Engineering",
    "Automotive Engineering": "Automobile Engineering",
    "Bio- Technology": "Bio-Technology",
    "Bio-technology": "Bio-Technology",
    "Biotechnology & Bio- Engineering": "Bio-Technology",
    "Biotechnology & Bio-engineering": "Bio-Technology",
    "Biotechnology & Bio-Engineering": "Bio-Technology",
    "Bio-medical Engineering": "Bio-Medical Engineering",
    "Biomedical Engineering": "Bio-Medical Engineering",
    "Analytics": "Information Technology (Data Analytics)",
    "B.plan": "Urban and Regional Planning",
    "Planning": "Urban and Regional Planning",
    "B.tech Cs-softwa Re Dev": "Computer Engineering (Software Product Development)",
    "B Tech (Hons) Computer Science and Engineering(Data Science)": "Computer Science and Engineering (Data Science)",
    "Ce Ca": "Civil Engineering with Computer Application",
    "Ce Se": "Civil Engineering",
    "Cmp in Med Engineering": "Computer Science and Medical Engineering",
    "Cs (Ai & Ds)": "Computer Science and Engineering (Artificial Intelligence and Data Science)",
    "Cs (Ai &": "Computer Science and Engineering (Artificial Intelligence and Data Science)",
    "Cs (AI and": "Computer Science and Engineering (Artificial Intelligence and Data Science)",
    "Cs Ai": "Computer Science and Engineering (Artificial Intelligence)",
    "Cs Aiml": "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "Cs Cc": "Computer Science and Engineering (Cloud Computing)",
    "Cs Cy": "Computer Science and Engineering (Cyber Security)",
    "Cs Ds": "Computer Science and Engineering (Data Science)",
    "Cs Iot": "Computer Science and Engineering (Internet of Things)",
    "Cs Ro": "Computer Science and Engineering (Robotics)",
    "Cs Sec": "Computer Science and Engineering (Cyber Security)",
    "Cs Tech (Pwd Only)": "Computer Science & Technology",
    "Cse Cb": "Computer Science and Business Systems",
    "Da": "Computer Science and Engineering (Data Analytics)",
    "Ec Vlsi": "Electronics and Communication Engineering (VLSI Design and Technology)",
    "Ee Cs": "Electrical Engineering and Computer Science",
    "Ele Veh": "Electrical Engineering (Electric Vehicle Technology)",
    "Es and Vlsi": "Embedded Systems and VLSI",
    "Me As": "Mechanical and Aerospace Engineering",
    "Vlsi": "VLSI Design and Technology",
    "Vr": "Information Technology (Augmented Reality and Virtual Reality)",
    "B.tech In Es And Vlsi": "Embedded Systems and VLSI",
    "Es And Vlsi": "Embedded Systems and VLSI",
    
    # New overrides
    "AI and Future Tech": "Computer Science and Engineering (Artificial Intelligence and Future Technologies)",
    "AI and ML": "Artificial Intelligence and Machine Learning",
    "Computer Science and Engineering (AI and Machine Learning)": "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "Computer Science and Engineering (AI/ML)": "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "Computer Science and Engineering (Aiml)": "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "Computer Science and Engineering (Cybsec)": "Computer Science and Engineering (Cyber Security)",
    "Data Sciences": "Computer Science and Engineering (Data Science)",
    "Electronics": "Electronics Engineering",
    "Life Style and Access": "Lifestyle and Accessory Design",
    "Life Style and Accessory Design": "Lifestyle and Accessory Design",
    "Industr Ial Design": "Industrial Design",
    "Commu Nicatio N Design": "Communication Design",
    "Medical Electronics": "Medical Electronics Engineering",
    "Productio N Engineering": "Production Engineering",
    "Pharma": "Pharmaceutical Engineering",
    
    # Baseline truncated names
    "Mechanical and Smart": "Mechanical and Smart Manufacturing",
    "Artificial Intelligence and Data": "Artificial Intelligence and Data Science",
    "Robotics and Artificial": "Robotics and Artificial Intelligence",
    "Electronics and Computer": "Electronics and Computer Engineering",
    "Computer Science and": "Computer Science and Engineering",
    "Electronics and": "Telecommunication Engineering",
    "Industrial Engineering and": "Industrial Engineering and Management",
    "Industrial Engineering &": "Industrial Engineering and Management",
    "Computer and Communication": "Computer and Communication Engineering"
}

# Short code mapping to full name (used for unmapped/generic codes in parentheses)
SHORT_CODE_MAP = {
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

def clean_typos(name):
    # Replace & with and
    name = name.replace('&', ' and ')
    
    # Common spacing issues / text wrapping errors in PDF extraction
    name = re.sub(r'\bDAT\s+A\s+SCIENCE\b', 'DATA SCIENCE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bD\s+ATA\s+SCIENCE\b', 'DATA SCIENCE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCYB\s+ER\s+SECURITY\b', 'CYBER SECURITY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bC\s+YBER\s+SECURITY\b', 'CYBER SECURITY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bBLO\s+CK\s+CHAIN\b', 'BLOCK CHAIN', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTI\s+FICIAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTI\s+FICAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bA\s+RTIFICIAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTIFICAL\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bARTIFICIA\s+L\b', 'ARTIFICIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bUNIVERISTY\b', 'UNIVERSITY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCOMMUNICATION\s+ENGG\b', 'COMMUNICATION ENGINEERING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCOMMUNICATIO\s+N\s+ENGG\b', 'COMMUNICATION ENGINEERING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCOMMUNICATIO\s+N\b', 'COMMUNICATION', name, flags=re.IGNORECASE)
    name = re.sub(r'\bENGG\b', 'ENGINEERING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bSOFTWA\s+RE\b', 'SOFTWARE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bSOFT\s+WARE\b', 'SOFTWARE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bSOF\s+TWARE\b', 'SOFTWARE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bINTERNE\s+T\b', 'INTERNET', name, flags=re.IGNORECASE)
    name = re.sub(r'\bELECTR\s+ONICS\b', 'ELECTRONICS', name, flags=re.IGNORECASE)
    name = re.sub(r'\bTELECOMMUNICAT\s+ION\b', 'TELECOMMUNICATION', name, flags=re.IGNORECASE)
    name = re.sub(r'\bTELECOMMUNIC\s+ATION\b', 'TELECOMMUNICATION', name, flags=re.IGNORECASE)
    name = re.sub(r'\bANLYTS\b', 'ANALYTICS', name, flags=re.IGNORECASE)
    name = re.sub(r'\bIND\s+USTRIAL\b', 'INDUSTRIAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bV\s+LSI\b', 'VLSI', name, flags=re.IGNORECASE)
    name = re.sub(r'\bINTEGTATED\b', 'INTEGRATED', name, flags=re.IGNORECASE)
    name = re.sub(r'\bMATHAMATICS\b', 'MATHEMATICS', name, flags=re.IGNORECASE)
    name = re.sub(r'\bVIRUTAL\b', 'VIRTUAL', name, flags=re.IGNORECASE)
    
    # New split word corrections
    name = re.sub(r'\bBIOTECHNOLOG\s+Y\b', 'BIOTECHNOLOGY', name, flags=re.IGNORECASE)
    name = re.sub(r'\bCLOU\s+D\b', 'CLOUD', name, flags=re.IGNORECASE)
    name = re.sub(r'\bMANUFACTURIN\s+G\b', 'MANUFACTURING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bPHARMACEUTIC\s+AL\b', 'PHARMACEUTICAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bENVIRONMENTA\s+L\b', 'ENVIRONMENTAL', name, flags=re.IGNORECASE)
    name = re.sub(r'\bINSTRUMENTATI\s+ON\b', 'INSTRUMENTATION', name, flags=re.IGNORECASE)
    name = re.sub(r'\bBIO-\s+ENGINEERING\b', 'BIO-ENGINEERING', name, flags=re.IGNORECASE)
    name = re.sub(r'\bI\s+OT\b', 'IoT', name, flags=re.IGNORECASE)
    name = re.sub(r'\bS\s+OFTWARE\b', 'SOFTWARE', name, flags=re.IGNORECASE)
    name = re.sub(r'\bDEV\s+OPS\b', 'DEVOPS', name, flags=re.IGNORECASE)
    
    # Abbreviation expansion to unify names and prevent repeats
    name = re.sub(r'\bAI\b', 'Artificial Intelligence', name, flags=re.IGNORECASE)
    name = re.sub(r'\bML\b', 'Machine Learning', name, flags=re.IGNORECASE)
    name = re.sub(r'\bDS\b', 'Data Science', name, flags=re.IGNORECASE)
    name = re.sub(r'\bDs\b', 'Data Science', name, flags=re.IGNORECASE)
    name = re.sub(r'\bIOT\b', 'Internet of Things', name, flags=re.IGNORECASE)
    name = re.sub(r'\bIoT\b', 'Internet of Things', name, flags=re.IGNORECASE)
    name = re.sub(r'\bVLSI\b', 'VLSI', name, flags=re.IGNORECASE)
    name = re.sub(r'\bVlsi\b', 'VLSI', name, flags=re.IGNORECASE)
    name = re.sub(r'\bAR\b', 'Augmented Reality', name, flags=re.IGNORECASE)
    name = re.sub(r'\bVR\b', 'Virtual Reality', name, flags=re.IGNORECASE)
    name = re.sub(r'\bMGMT\b', 'Management', name, flags=re.IGNORECASE)
    return name

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

def standardize_single_name(name):
    # 1. Check direct override mapping case-insensitively and using super_clean
    name_stripped = name.strip()
    name_lower = name_stripped.lower()
    for raw_k, clean_v in MANUAL_OVERRIDE_MAP.items():
        if name_lower == raw_k.lower().strip() or super_clean(name_stripped) == super_clean(raw_k):
            return clean_v
            
    # 2. Strip B Tech / Hons / in prefixes first!
    n = re.sub(r'^(B\s*TECH\s*\(?HONS\)?|B\.?\s*TECH\s*\(?HONS\)?|B\s*TECH\s*IN|B\.?\s*TECH\s*IN|BTECH\s*IN|B\s*TECH|B\.?\s*TECH|BTECH)\s+(?=\w)', '', name_stripped, flags=re.IGNORECASE).strip()
    n = clean_typos(n)
    
    # 3. Check if the remaining string is a short code (either in parens or alone)
    short_code = None
    m_paren = re.search(r'\(([A-Za-z0-9]{2,6})\)', n)
    if m_paren:
        short_code = m_paren.group(1).upper()
    else:
        m_direct = re.match(r'^([A-Za-z0-9]{2,6})(\s+in)?$', n, re.IGNORECASE)
        if m_direct:
            short_code = m_direct.group(1).upper()
            
    if short_code and short_code in SHORT_CODE_MAP:
        return SHORT_CODE_MAP[short_code]
        
    # 4. Standardize spacing around parentheses
    n = re.sub(r'\s*\(\s*', ' (', n)
    n = re.sub(r'\s*\)\s*', ')', n)
    n = re.sub(r'(\w)\(', r'\1 (', n)
    n = re.sub(r'\s+', ' ', n).strip()
    
    # 5. Correct words to Title Case with standard acronyms
    words = []
    for word in re.split(r'(\s+|[()&/])', n):
        if not word.strip():
            words.append(word)
            continue
        if word in ['(', ')', '&', '/']:
            words.append(word)
            continue
        
        w_lower = word.lower()
        if w_lower in ['and', 'of', 'in', 'including', 'with', 'for'] and len(words) > 0 and not words[-1].endswith('('):
            words.append(w_lower)
        else:
            if w_lower in ['vlsi']:
                words.append('VLSI')
            elif w_lower in ['iot']:
                words.append('IoT')
            elif w_lower in ['ai']:
                words.append('AI')
            elif w_lower in ['ml']:
                words.append('ML')
            elif w_lower in ['ar/vr']:
                words.append('AR/VR')
            elif w_lower in ['ar']:
                words.append('AR')
            elif w_lower in ['vr']:
                words.append('VR')
            elif w_lower in ['btech']:
                words.append('BTech')
            elif w_lower in ['devops']:
                words.append('DevOps')
            elif w_lower in ['pwd']:
                words.append('PWD')
            else:
                words.append(word.capitalize())
                
    res = "".join(words).strip()
    res = re.sub(r'\s+', ' ', res)
    res = res.replace("Engineering Engineering", "Engineering")
    
    # 6. Direct normalization rules using normalized string matching
    norm_lower = res.lower().strip()
    
    # Check overrides again on the normalized title-cased name
    for raw_k, clean_v in MANUAL_OVERRIDE_MAP.items():
        if norm_lower == raw_k.lower().strip() or super_clean(res) == super_clean(raw_k):
            return clean_v
            
    if norm_lower == "computer science":
        return "Computer Science"
    elif norm_lower == "planning" or norm_lower == "b.plan" or norm_lower == "b.plan.":
        return "Urban and Regional Planning"
    elif norm_lower == "automobile" or norm_lower == "automobile engineering" or norm_lower == "automotive" or norm_lower == "automotive engineering":
        return "Automobile Engineering"
        
    # Check more specific patterns first
    if "computer science" in norm_lower:
        if "artificial intelligence" in norm_lower and "future technologies" in norm_lower:
            return "Computer Science and Engineering (Artificial Intelligence and Future Technologies)"
        elif "artificial intelligence" in norm_lower and "machine learning" in norm_lower:
            return "Computer Science and Engineering (Artificial Intelligence and Machine Learning)"
        elif "artificial intelligence" in norm_lower and "data science" in norm_lower:
            return "Computer Science and Engineering (Artificial Intelligence and Data Science)"
        elif "internet of things" in norm_lower and "cyber security" in norm_lower:
            return "Computer Science and Engineering (Internet of Things & Cyber Security including Block Chain Technology)"
        elif "iot" in norm_lower and "cyber security" in norm_lower:
            return "Computer Science and Engineering (Internet of Things & Cyber Security including Block Chain Technology)"
        elif "cyber security" in norm_lower:
            return "Computer Science and Engineering (Cyber Security)"
        elif "data science" in norm_lower:
            return "Computer Science and Engineering (Data Science)"
        elif "artificial intelligence" in norm_lower:
            return "Computer Science and Engineering (Artificial Intelligence)"
        elif "business" in norm_lower:
            return "Computer Science and Business Systems"
        elif "design" in norm_lower:
            return "Computer Science and Design"
        elif "internet of things" in norm_lower or "iot" in norm_lower:
            return "Computer Science and Engineering (Internet of Things)"
        elif "cloud" in norm_lower:
            return "Computer Science and Engineering (Cloud Computing)"
        elif "blockchain" in norm_lower or "block chain" in norm_lower:
            return "Computer Science and Engineering (Blockchain)"
        elif "medical" in norm_lower:
            return "Computer Science and Medical Engineering"
        elif "information technology" in norm_lower:
            return "Computer Science and Information Technology"
        elif "technology" in norm_lower:
            return "Computer Science and Technology"
            
    # Non-computer science specific check
    if "artificial intelligence" in norm_lower and "machine learning" in norm_lower:
        return "Artificial Intelligence and Machine Learning"
    elif "artificial intelligence" in norm_lower and "data science" in norm_lower:
        return "Artificial Intelligence and Data Science"
        
    if "telecommunication" in norm_lower:
        return "Telecommunication Engineering"
        
    if "information science" in norm_lower:
        if "technology" in norm_lower:
            return "Information Science and Technology"
        return "Information Science and Engineering"
        
    if "electronics" in norm_lower and "communication" in norm_lower:
        if "vlsi" in norm_lower:
            return "Electronics and Communication Engineering (VLSI Design and Technology)"
        elif "advanced" in norm_lower:
            return "Electronics and Communication (Advanced Communication Technology)"
        elif "industrial" in norm_lower:
            return "Electronics and Communication Engineering (Industrial Integrated)"
        return "Electronics and Communication Engineering"
        
    if "electronics" in norm_lower and "instrumentation" in norm_lower:
        return "Electronics and Instrumentation Engineering"
    elif "electrical" in norm_lower and "electronics" in norm_lower:
        return "Electrical and Electronics Engineering"
    elif "mechanical" in norm_lower and "aerospace" in norm_lower:
        return "Mechanical and Aerospace Engineering"
    elif "robotics" in norm_lower and "automation" in norm_lower:
        return "Robotics and Automation"
    elif "robotics" in norm_lower and "artificial intelligence" in norm_lower:
        return "Robotics and Artificial Intelligence"
    elif "biomedical" in norm_lower and "robotic" in norm_lower:
        return "Biomedical and Robotic Engineering"
    elif "bio" in norm_lower and "technology" in norm_lower:
        return "Bio-Technology"
    elif "bio" in norm_lower and "medical" in norm_lower:
        return "Bio-Medical Engineering"
    elif "civil" in norm_lower and "kannada" in norm_lower:
        return "Civil Engineering (Kannada Medium)"
    elif "mechanical" in norm_lower and "kannada" in norm_lower:
        return "Mechanical Engineering (Kannada Medium)"
    elif "civil" in norm_lower and "computer application" in norm_lower:
        return "Civil Engineering with Computer Application"
    elif "civil" in norm_lower and "environmental" in norm_lower:
        return "Civil Environmental Engineering"
    elif "environmental" in norm_lower:
        return "Environmental Engineering"
    elif "mechatronics" in norm_lower:
        return "Mechatronics Engineering"
    elif "mathematics" in norm_lower and "computing" in norm_lower:
        return "Mathematics and Computing"
    elif "mathamatics" in norm_lower and "computing" in norm_lower:
        return "Mathematics and Computing"
    elif "industrial" in norm_lower and "production" in norm_lower:
        return "Industrial and Production Engineering"
    elif "industrial" in norm_lower and "management" in norm_lower:
        return "Industrial Engineering and Management"
    elif "textile" in norm_lower:
        return "Textiles Technology"
    elif "vlsi" in norm_lower:
        return "VLSI Design and Technology"
    elif "ar/vr" in norm_lower:
        return "Information Technology (Augmented Reality and Virtual Reality)"
    elif "augmented reality" in norm_lower:
        return "Information Technology (Augmented Reality and Virtual Reality)"
    elif "data analytics" in norm_lower:
        return "Information Technology (Data Analytics)"
        
    return res

def run_standardization():
    print("Loading seat_matrix_data.json...")
    with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
        sm_data = json.load(f)
        
    # Load unified course mapping
    mapping = {}
    import os
    if os.path.exists("course_standardization_map.json"):
        print("Loading course_standardization_map.json...")
        with open("course_standardization_map.json", "r", encoding="utf-8") as f:
            mapping = json.load(f)
    else:
        print("Warning: course_standardization_map.json not found! Falling back to dynamic standardization.")
        
    # Step 1: Collect all unique course names from the seat matrix
    unique_names = set()
    for col in sm_data["colleges"]:
        for c in col["courses"]:
            unique_names.add(c["course_name"])
            
    print(f"Found {len(unique_names)} unique course names in seat matrix.")
    
    # Step 2: Create a mapping of old_name -> standardized_name
    course_name_mapping = {}
    for old_name in unique_names:
        if old_name in mapping:
            course_name_mapping[old_name] = mapping[old_name]
        else:
            std = standardize_single_name(old_name)
            print(f"Warning: '{old_name}' not found in map. Standardized dynamically to '{std}'.")
            course_name_mapping[old_name] = std
            
    # Print the mapping changes
    changes = {k: v for k, v in course_name_mapping.items() if k != v}
    print(f"Mapping will change {len(changes)} course names:")
    for k, v in sorted(changes.items()):
        print(f"  '{k}' -> '{v}'")
        
    # Step 3: Apply the mapping to all courses in seat_matrix_data.json
    total_modified = 0
    for col in sm_data["colleges"]:
        for c in col["courses"]:
            old_name = c["course_name"]
            new_name = course_name_mapping[old_name]
            if old_name != new_name:
                c["course_name"] = new_name
                total_modified += 1
                
    print(f"Standardized {total_modified} courses across all colleges.")
    
    # Save the updated database
    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(sm_data, f, indent=2, ensure_ascii=False)
        
    print("Saved standardized seat_matrix_data.json successfully!")

if __name__ == "__main__":
    run_standardization()
