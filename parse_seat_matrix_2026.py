import json
import os
import re
import pypdf

# Define constants
PDF_PATH = r"E:\Antigravity\archive\2026\Eng_Seat_Matrix_final_30062026english.pdf"
EXISTING_2026_JSON = r"E:\Antigravity\seat_matrix_data_2026.json"
BASE_2025_JSON = r"E:\Antigravity\seat_matrix_data.json"
OUTPUT_2026_JSON = r"E:\Antigravity\seat_matrix_data_2026.json"
OUTPUT_BASELINE_JSON = r"E:\Antigravity\baseline\seat_matrix_data_2026.json"

# Load course standardization map
COURSE_MAP = {}
map_path = r"E:\Antigravity\course_standardization_map.json"
if os.path.exists(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        raw_map = json.load(f)
        for k, v in raw_map.items():
            COURSE_MAP[k.upper().strip()] = v

# Add specific overrides
COURSE_MAP['COMPUTER SCIENCE AND ENGG (ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING)'] = 'Computer Science and Engineering (Artificial Intelligence and Machine Learning)'
COURSE_MAP['ARTIFICIAL INTELLIGENCE AND MACHINELEARNING'] = 'Artificial Intelligence and Machine Learning'
COURSE_MAP['MECHAMCAL ENGINEERING'] = 'Mechanical Engineering'
COURSE_MAP['TEXTILES TECTINOLOGY'] = 'Textile Technology'

# Hyderabad-Karnataka (HK) region districts
HK_DISTRICTS = {"Bidar", "Kalaburagi", "Yadgir", "Raichur", "Koppal", "Ballari", "Vijayanagara"}

# New 2026 Colleges metadata
NEW_COLLEGES = {
    "futureforgeengineering": {
        "kea_code": "E323",
        "college_number": 323,
        "college_name": "Future Forge Engineering Academy",
        "district": "Dharwad",
        "established": 2026
    },
    "isbrandtechnology": {
        "kea_code": "E324",
        "college_number": 324,
        "college_name": "ISBR College of Engineering and Technology",
        "district": "Bangalore",
        "established": 2026
    },
    "dhanwantari": {
        "kea_code": "E325",
        "college_number": 325,
        "college_name": "Dhanwantari Institute of Technology",
        "district": "Bangalore",
        "established": 2026
    },
    "krupanidhi": {
        "kea_code": "E326",
        "college_number": 326,
        "college_name": "Krupanidhi Institute of Technology",
        "district": "Bangalore",
        "established": 2026
    },
    "agmandtechnologybelgaum": {
        "kea_code": "E327",
        "college_number": 327,
        "college_name": "AGM College of Engineering and Technology, Belgaum",
        "district": "Belgaum",
        "established": 2026
    },
    "shriswaminagabhushangurukulandtechnology": {
        "kea_code": "E328",
        "college_number": 328,
        "college_name": "Shri Swami Nagabhushan Gurukul College of Engineering and Technology",
        "district": "Bijapur",
        "established": 2026
    },
    "bms": {
        "kea_code": "E318",
        "college_number": 318,
        "college_name": "BMS University",
        "district": "Bangalore",
        "established": 2026
    },
    "cmn": {
        "kea_code": "E322",
        "college_number": 322,
        "college_name": "C M N Institute Of Technology",
        "district": "Bangalore",
        "established": 2026
    },
    "koshys": {
        "kea_code": "E223",
        "college_number": 82,
        "college_name": "KOSHYS TNSTITUTE OF TECHNOLOGY",
        "district": "Bangalore",
        "established": 2026
    }
}

# OCR corrections mapping
mapping = {
    'l': '1', 'i': '1', 'I': '1', 't': '1', 'L': '1', 'T': '1',
    'J': '3', 'j': '3',
    'o': '0', 'O': '0',
    's': '5', 'S': '5',
    'z': '2', 'Z': '2',
    'g': '9', 'G': '9',
    'b': '6', 'B': '6',
    'r': '1', 'R': '1',
    ')': '3',
    '(': '0',
    'a': '7', 'A': '7',
    'u': '0', 'U': '0',
    'f': '3', 'F': '3',
    '<': '5',
    '?': '2',
    '|': '1',
    '&': '8',
    '!': '1',
    'h': '6',
    'C': '0',
    'c': '0',
    'N': '4',
    'n': '4'
}

def clean_ocr_number(s):
    s_clean = s.replace(",", "").replace(".", "").replace("-", "").replace("'", "").replace("`", "").replace("/", "").replace("\\", "").replace("+", "").replace("*", "").replace("=", "").replace("_", "").replace("|", "1").replace("^", "").replace(":", "").replace(";", "").strip()
    if s_clean.startswith("(") and s_clean.endswith(")"):
        s_clean = s_clean[1:-1]
    cleaned = ""
    for char in s_clean:
        if char.isdigit():
            cleaned += char
        elif char in mapping:
            cleaned += mapping[char]
    if cleaned:
        return int(cleaned)
    return 0

def is_garbled_number(token):
    t = token.strip()
    if not t:
        return False
    if t.lower() in ["ins", "lns", "tot", "total", "t0t", "t0tal"]:
        return False
    if t.isdigit():
        return True
    if len(t) == 1:
        return t.isdigit() or t in mapping
    t_clean = t.replace(",", "").replace(".", "").replace("-", "").replace("'", "").replace("`", "").replace("/", "").replace("\\", "").replace("+", "").replace("*", "").replace("=", "").replace("_", "").replace("|", "1").replace("^", "").replace(":", "").replace(";", "").strip()
    if t_clean.startswith("(") and t_clean.endswith(")"):
        t_clean = t_clean[1:-1]
    if not t_clean:
        return False

    return all(c.isdigit() or c in mapping for c in t_clean) and len(t_clean) <= 4

def clean_ocr_serial(s):
    s = s.replace("I", "1").replace("l", "1").replace("O", "0").replace("o", "0")
    s = s.replace("E", "8").replace("e", "8").replace("B", "8").replace("b", "8")
    s = s.replace("S", "5").replace("s", "5").replace("G", "6").replace("g", "6")
    s = s.replace("Z", "2").replace("z", "2")
    if len(s) == 4 and s.startswith("1") and s[1:].isdigit() and 100 <= int(s[1:]) <= 153:
        s = s[1:]
    return s

def is_valid_course_prefix(token):
    token = token.strip().lower()
    if not token:
        return False
    if token.isdigit():
        return True
    if re.match(r'^[ivxc]+$', token):
        return True
    if len(token) == 1 and not token.isalnum():
        return True
    if len(token) == 2 and ((token[0].isalpha() and token[1].isdigit()) or (token[0].isdigit() and token[1].isalpha())):
        return True
    if len(token) <= 3 and all(c in 'ivxljzrtnm' for c in token):
        return True
    return False

def clean_college_name(name):
    name = name.lower()
    # Strip KEA code in parentheses (e.g. (e003) or (e061))
    name = re.sub(r'\(e\d{3}\)', '', name)
    name = re.sub(r'[^a-z0-9]', '', name)
    
    # Avoid double replacement of "formerly" when replacing "ormerly"
    name = name.replace("formerly", "x_xyz_x")
    name = name.replace("ormerly", "formerly")
    name = name.replace("x_xyz_x", "formerly")
    
    # 1. Apply overrides FIRST (before removing generic words)
    overrides = {
        "chichamagalur": "chickamagalur",
        "anwartik": "anuvartik",
        "bharatesii": "bharatesh",
        "cawery": "cauvery",
        "lorge": "forge",
        "jaln": "jain",
        "shrisrvaminagabhushan": "shriswaminagabhushan",
        "iiassan": "hassan",
        "iassan": "hassan",
        "constittent": "constituent",
        "chikaballaptira": "chikaballapura",
        "chikaballaptura": "chikaballapura",
        "engiiieering": "engineering",
        "nlosale": "mosale",
        "engineerjng": "engineering",
        "coltege": "college",
        "technolory": "technology",
        "rechnology": "technology",
        "enginieering": "engineering",
        "vijayaptira": "vijayapura",
        "ypdrpghallakatti": "vpdrpghalakatti",
        "autonomoiis": "autonomous",
        "autonomois": "autonomous",
        "autonomoijs": "autonomous",
        "sirnvisvesvaraya": "sirmvisvesvaraya",
        "ruraiautonomous": "ruralautonomous",
        "afitonomous": "autonomous",
        "technologp": "technology",
        "ilulkoti": "hulkoti",
        "mahabalesrvarappa": "mahabaleswarappa",
        "llfs": "lfs",
        "yardhaka": "vardhaka",
        "banhval": "bantwal",
        "iiibk": "hkbk",
        "univesity": "university",
        "universify": "university",
        "trngineering": "engineering",
        "nlurugharajendra": "murugharajendra",
        "hnn": "drhnnational",
        "iiarsha": "harsha",
        "nidasoshiv": "hirasugarnidasoshi",
        "nidasoshi": "hirasugarnidasoshi",
        "cotlege": "college",
        "collegc": "college",
        "tjniversity": "university",
        "tiniversity": "university",
        "tintversity": "university",
        "fntversity": "university",
        "mlnstitute": "minstitute",
        "lnstitute": "institute",
        "tnstitute": "institute",
        "madhrva": "madhwa",
        "gandiii": "gandhi",
        "teciinology": "technology",
        "ttte": "the",
        "e066": "",
        "nlysore": "mysore",
        "technologtcal": "technological",
        "srijagadgurunlurugharajendrauniversitysjminstituteoftechnology": "sjm",
        "srijagadgurumurugharajendrauniversitysjminstituteoftechnology": "sjm",
        "intitute": "institute",
        "bngineering": "engineering",
        "n{andya": "mandya",
        "nandya": "mandya",
        "autonoi\\ious": "autonomous",
        "autonoi\\ous": "autonomous",
        "autonoi/ous": "autonomous",
        "autonoi/ious": "autonomous",
        "autonoious": "autonomous",
        "autonomoiis": "autonomous",
        "aiitonomous": "autonomous",
        "autonoiious": "autonomous",
        "rmaiah": "ramaiah",
        "applted": "applied",
        "adhichunchanagiriuniversityformerlybgsinstituteoftechnologybgnagara": "bgs",
        "adhichunchanagiriuniversityformerlybgsinstituteoftechnology": "bgs",
        "adhichunchanagiriuniversitybgs": "bgs",
        "adhichunchanagirifformerlybgsbgnagara": "bgs",
        "isbrand": "isbr"
    }
    for k, v in overrides.items():
        name = name.replace(k, v)
        
    # 2. Remove generic words AFTER overrides
    for w in ["collegeofengineering", "instituteoftechnology", "engineeringcollege", "bangalore", "bengaluru", "mangalore", "mysore", "mysuru", "management", "society", "association", "education", "educational", "trust", "academy", "school", "university", "campus"]:
        name = name.replace(w, "")
        
    return name

def standardize_college_name(name):
    if not name:
        return name
    # Clean dots/spaces in common abbreviations (e.g. S.J B., S J C)
    name = re.sub(r'\bS\.?\s*J\.?\s*B(?:\.|\b)', 'SJB', name, flags=re.IGNORECASE)
    name = re.sub(r'\bS\.?\s*J\.?\s*C(?:\.|\b)', 'SJC', name, flags=re.IGNORECASE)
    # Clean common spelling typos
    name = name.replace("Technolory", "Technology")
    name = name.replace("Technoloy", "Technology")
    return name

def clean_course_name(name):
    name = name.upper().strip()
    
    # Standardize common OCR typos in course names
    typos = {
        "ENGINEEZUNG": "ENGINEERING",
        "ENGINEEZUING": "ENGINEERING",
        "ENGINEERIN G": "ENGINEERING",
        "ENC,G": "ENGG",
        "ENCG": "ENGG",
        "COMMTJMCATION": "COMMUNICATION",
        "COMMUMCATION": "COMMUNICATION",
        "COMMI]MCATION": "COMMUNICATION",
        "LEARMNG": "LEARNING",
        "LEARMING": "LEARNING",
        "ELECTZUCAL": "ELECTRICAL",
        "MACHINELEARNING": "MACHINE LEARNING",
        "SECTJRITY": "SECURITY",
        "ELECTROMCS": "ELECTRONICS",
        "COMMTJNICATION": "COMMUNICATION",
        "MECFLA.NICAL": "MECHANICAL",
        "MECFLANICAL": "MECHANICAL",
        "INSTRIJMENTATION": "INSTRUMENTATION"
    }
    for k, v in typos.items():
        name = name.replace(k, v)

    # Strip any leading quotes or stray symbols first
    name = re.sub(r"^['\"`\s\-\.\,\)\(\[\]]+", "", name)
    # Strip any single character prefix followed by a space (e.g. "J ", "I ", "1 ")
    name = re.sub(r'^[A-Z0-9\)\(\[\]\-\.\,\?\!\@\#\$\%\^\&\*\+\=]\s+', '', name)
    # Strip leading serial numbers, possibly split by spaces (e.g. "I 2 ", "I 1 ")
    name = re.sub(r'^(?:[I1lJ]|\d)+\s+(?:[I1lJ]|\d)*(?:\s+|\.)', '', name)
    name = re.sub(r'^[A-Z0-9]*[0-9][A-Z0-9]*(?:\s+|\.)', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    if name in COURSE_MAP:
        return COURSE_MAP[name]
    return name.title()

def load_2025_metadata():
    with open(BASE_2025_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    colleges_map = {}
    for col in data.get("colleges", []):
        col["college_name"] = standardize_college_name(col.get("college_name"))
        clean_n = clean_college_name(col["college_name"])
        ann = col.get("annexure", "A").upper()
        # Map both (clean_name, annexure) and clean_name alone
        colleges_map[(clean_n, ann)] = col
        if clean_n not in colleges_map:
            colleges_map[clean_n] = col
    return colleges_map

def load_existing_2026_cutoffs():
    if not os.path.exists(EXISTING_2026_JSON):
        return {}
    try:
        with open(EXISTING_2026_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        cutoffs_map = {}
        for col in data.get("colleges", []):
            kea_code = col.get("kea_code")
            if not kea_code:
                continue
            for c in col.get("courses", []):
                c_name = clean_course_name(c["course_name"])
                key = (kea_code, c_name)
                cutoffs_map[key] = {
                    "round1_cutoff": c.get("round1_cutoff") or {},
                    "round2_cutoff": c.get("round2_cutoff") or {},
                    "round3_cutoff": c.get("round3_cutoff") or {},
                    "mock_round1_cutoff": c.get("mock_round1_cutoff") or {}
                }
        return cutoffs_map
    except Exception as e:
        print(f"Warning loading existing cutoffs: {e}")
        return {}

def match_college(pdf_name, current_annexure, colleges_2025):
    # Reject generic course/header words
    words = [w.lower() for w in re.findall(r'[a-zA-Z]+', pdf_name)]
    generic_course_words = {
        "college", "engineering", "technology", "institute", "of", "and", "the", "school", "academy", "university", "campus",
        "computer", "science", "information", "business", "systems", "design", "civil", "mechanical", "electrical", "electronics",
        "communication", "aeronautical", "automobile", "marine", "textile", "biotechnology", "chemical", "industrial", "production",
        "robotics", "artificial", "intelligence", "machine", "learning", "data", "sciences", "cyber", "security", "internet",
        "things", "blockchain", "iot", "design", "planning", "architecture", "btech", "mtech", "b", "m", "tech", "hons",
        "aided", "unaided", "government", "constituent", "minority", "private", "deemed", "seats", "intake", "total"
    }
    if all(w in generic_course_words for w in words):
        return None

    pdf_clean = clean_college_name(pdf_name)
    pdf_clean_raw = re.sub(r'[^a-z0-9]', '', pdf_name.lower())
    
    # Specific override for VTU Gokak (E315 / E317)
    if "gokak" in pdf_clean_raw or "gokak" in pdf_clean:
        if current_annexure.upper() == "A":
            return {
                "kea_code": "E315",
                "college_number": 315,
                "college_name": "VTU Constituent Engineering College, Gokak",
                "district": "Belgaum",
                "established": 2026,
                "annexure": "A",
                "college_type": "Government"
            }
        elif current_annexure.upper() == "Z":
            return {
                "kea_code": "E317",
                "college_number": 317,
                "college_name": "VTU Constituent Engineering College, Gokak",
                "district": "Belgaum",
                "established": 2026,
                "annexure": "Z",
                "college_type": "Government College with Higher Fees"
            }
            
    # Specific override for University of Mysuru (E283 / E322)
    if "universityofmysuru" in pdf_clean_raw or "universityofmysore" in pdf_clean_raw:
        if current_annexure.upper() == "A":
            return {
                "kea_code": "E283",
                "college_number": 283,
                "college_name": "University of Mysuru",
                "district": "Mysore",
                "established": 2025
            }
        elif current_annexure.upper() == "Z":
            return {
                "kea_code": "E321",
                "college_number": 321,
                "college_name": "University of Mysuru",
                "district": "Mysore",
                "established": 2026
            }



    # Specific override for RV University campuses
    if "rvuniversity" in pdf_clean_raw or "rvuni" in pdf_clean_raw:
        if "nanjanagudu" in pdf_clean_raw or "nanjangud" in pdf_clean_raw:
            return {
                "kea_code": "E316",
                "college_number": 316,
                "college_name": "RV University, Nanjanagudu Campus",
                "district": "Mysore",
                "established": 2026,
                "annexure": "O",
                "college_type": "Private University"
            }
        else:
            return {
                "kea_code": "E285",
                "college_number": 285,
                "college_name": "RV University, Bengaluru Campus",
                "district": "Bangalore",
                "established": 2021,
                "annexure": "O",
                "college_type": "Private University"
            }

    # Specific override for Srinivas Institute of Technology vs Srinivas University
    if "srinivasinstituteoftechnology" in pdf_clean_raw:
        return colleges_2025.get(("srinivas", "C"))
        
    # Specific override for constituent Ramaiah
    if "constituent" in pdf_clean_raw and "ramaiah" in pdf_clean_raw:
        return {
            "kea_code": "E319",
            "college_number": 319,
            "college_name": "Ramaiah University College of Engineering",
            "district": "Bangalore",
            "established": 2026,
            "annexure": "O",
            "college_type": "Private University"
        }
        
    # Specific override for SJM
    if "srijagadgurumurugha" in pdf_clean_raw or "sjminstitute" in pdf_clean_raw or "srijagadgurunlurugha" in pdf_clean_raw or "sjm" in pdf_clean_raw:
        return {
            "kea_code": "E063",
            "college_number": 63,
            "college_name": "Sri Jagadguru Murugarajendra University (SJM Institute of Technology)",
            "district": "Chitradurga",
            "established": 1980,
            "annexure": "O",
            "college_type": "Private University"
        }
        
    if "msramaiahunivesityofapplted" in pdf_clean or "ramaiah" in pdf_clean and "applied" in pdf_clean:
        return colleges_2025.get(("msramaiahofappliedsciences", "O")) or colleges_2025.get("msramaiahofappliedsciences")

    # Specific override for CMR Institute of Technology (E097) vs CMR University (E257)
    if "cmr" in pdf_clean_raw:
        if current_annexure.upper() == "C":
            return colleges_2025.get(("cmrkundalahallivillage", "C"))
        elif current_annexure.upper() == "O":
            return colleges_2025.get(("cmr", "O"))

    # 1. Search new colleges first
    for k, metadata in NEW_COLLEGES.items():
        if pdf_clean == k:
            return metadata
            
    # 2. Search by (clean_name, annexure) exactly
    key = (pdf_clean, current_annexure.upper())
    if key in colleges_2025:
        return colleges_2025[key]
        
    # 3. Search by clean_name exactly
    if pdf_clean in colleges_2025:
        return colleges_2025[pdf_clean]
    
    # 4. Substring matching with annexure (only if clean name length >= 4)
    for k, col in colleges_2025.items():
        if isinstance(k, tuple):
            name_clean, ann = k
            if ann == current_annexure.upper():
                if len(name_clean) >= 4 and len(pdf_clean) >= 4:
                    if name_clean in pdf_clean or pdf_clean in name_clean:
                        return col
                    
    # 5. Substring matching without annexure (only if clean name length >= 4)
    for k, col in colleges_2025.items():
        if isinstance(k, str):
            if len(k) >= 4 and len(pdf_clean) >= 4:
                if k in pdf_clean or pdf_clean in k:
                    return col
                
    # 6. Word overlap with annexure (only count words of length >= 3 to prevent matching single letters)
    pdf_words = set(w for w in re.findall(r'[a-z0-9]+', pdf_name.lower()) if len(w) >= 3)
    generic = {"college", "engineering", "technology", "institute", "of", "and", "the", "society", "societys", "education", "educational", "trust", "trusts", "autonomous", "aided", "unaided", "private", "government", "govt", "management", "association", "academy", "school", "university", "campus"}
    pdf_words -= generic
    
    best_match = None
    best_overlap = 0
    for k, col in colleges_2025.items():
        if isinstance(k, tuple):
            name_clean, ann = k
            if ann == current_annexure.upper():
                col_words = set(w for w in re.findall(r'[a-z0-9]+', col["college_name"].lower()) if len(w) >= 3) - generic
                overlap = len(pdf_words & col_words)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = col
                    
    if best_overlap >= 2:
        return best_match
        
    # 7. Word overlap without generic words
    best_match = None
    best_overlap = 0
    for k, col in colleges_2025.items():
        if isinstance(k, str):
            col_words = set(w for w in re.findall(r'[a-z0-9]+', col["college_name"].lower()) if len(w) >= 3) - generic
            overlap = len(pdf_words & col_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = col
                
    if best_overlap >= 2:
        return best_match
        
    return None

def get_standard_splits(ann, intake, kea_code=None):
    kea = 0
    comedk = 0
    mgmt = 0
    snq = max(1, int(intake * 0.05 + 0.5))
    
    if ann in ["A", "M", "Z"]:
        kea = intake
    elif ann == "B":
        kea = int(intake * 0.95 + 0.5)
        mgmt = intake - kea
    elif ann == "C":
        kea = int(intake * 0.45 + 0.5)
        comedk = int(intake * 0.30 + 0.5)
        mgmt = intake - kea - comedk
    elif ann == "D":
        kea = int(intake * 0.40 + 0.5)
        comedk = int(intake * 0.30 + 0.5) # KRLMP
        mgmt = intake - kea - comedk
    elif ann in ["O", "P"]:
        if ann == "O":
            kea = int(intake * 0.40 + 0.5)
        else:
            if kea_code == "E017":
                kea = int(intake * 0.40 + 0.5)
            else:
                kea = int(intake * 0.25 + 0.5)
            
    return kea, comedk, mgmt, snq

def align_seat_tokens(ann, intake, seats, expected_n, is_hk_college=False, kea_code=None):
    best_align = seats
    
    if len(seats) == expected_n + 1:
        best_align = seats[:-1]
        min_penalty = 999999
        
        for i in range(0, len(seats)):
            candidate = seats[:i] + seats[i+1:]
            cand_intake = candidate[0]
            
            std_kea, std_comedk, std_mgmt, std_snq = get_standard_splits(ann, cand_intake, kea_code)
            std_ph = int(std_kea * 0.05 + 0.5)
            std_spl = 1 if std_kea >= 60 else 0
            
            p = abs(candidate[1] - std_kea) + abs(candidate[2] - std_ph) + abs(candidate[3] - std_spl)
            if len(candidate) >= 8: p += abs(candidate[7] - std_comedk)
            if len(candidate) >= 9: p += abs(candidate[8] - std_mgmt)
            if len(candidate) >= 10: p += abs(candidate[9] - std_snq)
            
            # Consistency penalty
            hk_val = candidate[4]
            rk_val = candidate[5]
            tot_val = candidate[6]
            kea_val = candidate[1]
            ph_val = candidate[2]
            spl_val = candidate[3]
            
            std_hk_val = int(tot_val * 0.70 + 0.5) if is_hk_college else int(tot_val * 0.08 + 0.5)
            std_rk_val = tot_val - std_hk_val
            
            consistency_err = abs(hk_val + rk_val - tot_val)
            consistency_err += abs(ph_val + spl_val + tot_val - kea_val)
            consistency_err += abs(hk_val - std_hk_val) + abs(rk_val - std_rk_val)
            
            p += consistency_err
            if p < min_penalty:
                min_penalty = p
                best_align = candidate

    elif len(seats) == expected_n - 1:
        best_align = seats + [0]
        min_penalty = 999999
        std_kea, std_comedk, std_mgmt, std_snq = get_standard_splits(ann, intake, kea_code)
        std_ph = int(std_kea * 0.05 + 0.5)
        std_spl = 1 if std_kea >= 60 else 0
        
        for i in range(1, expected_n):
            candidate = seats[:i] + [0] + seats[i:]
            p = abs(candidate[1] - std_kea) + abs(candidate[2] - std_ph) + abs(candidate[3] - std_spl)
            if len(candidate) >= 8: p += abs(candidate[7] - std_comedk)
            if len(candidate) >= 9: p += abs(candidate[8] - std_mgmt)
            if len(candidate) >= 10: p += abs(candidate[9] - std_snq)
            
            # Consistency penalty
            hk_val = candidate[4]
            rk_val = candidate[5]
            tot_val = candidate[6]
            kea_val = candidate[1]
            ph_val = candidate[2]
            spl_val = candidate[3]
            
            if i == 4:
                hk_val = max(0, tot_val - rk_val)
            elif i == 5:
                rk_val = max(0, tot_val - hk_val)
            elif i == 6:
                tot_val = hk_val + rk_val
                
            consistency_err = abs(hk_val + rk_val - tot_val)
            consistency_err += abs(ph_val + spl_val + tot_val - kea_val)
            
            std_hk_val = int(tot_val * 0.70 + 0.5) if is_hk_college else int(tot_val * 0.08 + 0.5)
            std_rk_val = tot_val - std_hk_val
            consistency_err += abs(hk_val - std_hk_val) + abs(rk_val - std_rk_val)
            
            p += consistency_err
            if i == expected_n - 1:
                p -= 1
                
            if p < min_penalty:
                min_penalty = p
                best_align = candidate

    # 3. Post-alignment Intake Correction
    standard_intakes = [15, 25, 35, 45, 55, 65, 75, 85, 95] + list(range(10, 3001, 10))
    non_std_kea = [58, 59, 68, 69, 118, 119, 128, 129, 138, 139, 198, 199]
    standard_intakes.extend(non_std_kea)
    if best_align and best_align[0] not in standard_intakes:
        best_intake = best_align[0]
        min_diff = 999999
        for cand_intake in standard_intakes:
            std_kea, std_comedk, std_mgmt, std_snq = get_standard_splits(ann, cand_intake)
            diff = 0
            if len(best_align) >= 2: diff += abs(best_align[1] - std_kea)
            if len(best_align) >= 8: diff += abs(best_align[7] - std_comedk) if ann in ["C", "D"] else abs(best_align[7] - std_mgmt)
            if len(best_align) >= 9: diff += abs(best_align[8] - std_mgmt) if ann in ["C", "D"] else 0
            if len(best_align) >= 10:
                diff += abs(best_align[9] - std_snq)
            elif len(best_align) >= 9 and ann not in ["C", "D"]:
                diff += abs(best_align[8] - std_snq)
                
            if diff < min_diff:
                min_diff = diff
                best_intake = cand_intake
        best_align[0] = best_intake

    return best_align

def sanitize_course_seats(ann, district, intake, parsed_seats, kea_code=None, course_name=""):
    std_kea, std_comedk, std_mgmt, std_snq = get_standard_splits(ann, intake, kea_code)
    
    # Specific override for SJCE E021 course 7 (Industrial & Production Engineering) HK seats
    if kea_code == "E021" and "indust" in course_name.lower() and "production" in course_name.lower():
        if intake == 60:
            parsed_seats["kea_hk"] = 5
            parsed_seats["kea_rk"] = 49
    
    if ann in ["B", "C", "D"]:
        # COMEDK/cat2 seats are always mathematically exact (30% for C/D, 0% for B)
        comedk = std_comedk
        if intake % 60 == 0:
            kea = std_kea
            mgmt = std_mgmt
        else:
            kea = parsed_seats.get("total_kea_seats", std_kea)
            if kea <= 0 or abs(kea - std_kea) > 5:
                kea = std_kea
            mgmt = parsed_seats.get("cat3_seats", std_mgmt)
            if mgmt < 0 or abs(mgmt - std_mgmt) > 5:
                mgmt = std_mgmt
    else:
        kea = parsed_seats.get("total_kea_seats", std_kea)
        if kea <= 0 or abs(kea - std_kea) > 5:
            kea = std_kea
            
        comedk = parsed_seats.get("cat2_seats", std_comedk)
        if comedk < 0 or abs(comedk - std_comedk) > 5:
            comedk = std_comedk
            
        mgmt = parsed_seats.get("cat3_seats", std_mgmt)
        if mgmt < 0 or abs(mgmt - std_mgmt) > 5:
            mgmt = std_mgmt
        
    # Enforce exact SNQ rule for intakes that are multiples of 20
    if intake % 20 == 0:
        snq = intake // 20
    else:
        snq = parsed_seats.get("snq_5pct", std_snq)
        if snq <= 0 or abs(snq - std_snq) > 1:
            snq = std_snq
        
    ph = parsed_seats.get("kea_ph", 0)
    spl = parsed_seats.get("kea_spl", 0)
    hk = parsed_seats.get("kea_hk", 0)
    rk = parsed_seats.get("kea_rk", 0)
    tot = parsed_seats.get("kea_tot", hk + rk)
    
    # Reconstruct PH/SPL if they are mathematically inconsistent
    std_ph = int(kea * 0.05 + 0.5)
    std_spl = 1 if kea >= 60 else 0
    
    if ph < 0 or ph > kea or abs(ph - std_ph) > 2:
        ph = std_ph
    if spl < 0 or spl > 5 or abs(spl - std_spl) > 2:
        spl = std_spl
        
    std_tot = kea - ph - spl
    if abs(tot - std_tot) > 5:
        tot = std_tot
        
    # Enforce HK + RK against TOT
    is_hk_college = district in HK_DISTRICTS
    if hk + rk != tot or hk < 0 or rk < 0:
        std_hk = tot * 0.70 if is_hk_college else tot * 0.08
        if abs(hk - std_hk) <= 1.5:
            rk = tot - hk
        elif abs(rk - (tot - std_hk)) <= 1.5:
            hk = tot - rk
        else:
            if hk >= 0 and rk >= 0 and hk + rk > 0:
                tot = hk + rk
            else:
                if is_hk_college:
                    hk = int(tot * 0.70 + 0.5)
                else:
                    hk = int(tot * 0.08 + 0.5)
                rk = tot - hk
        
    # Ensure components sum to KEA total
    if ph + spl + tot != kea:
        if hk + rk == tot:
            if kea - tot - spl >= 0:
                ph = kea - tot - spl
            elif kea - tot - ph >= 0:
                spl = kea - tot - ph
        else:
            tot = kea - ph - spl
            if is_hk_college:
                hk = int(tot * 0.70 + 0.5)
            else:
                hk = int(tot * 0.08 + 0.5)
            rk = tot - hk

    if hk + rk != tot:
        rk = tot - hk
        
    # Re-enforce KEA = PH + SPL + TOT
    kea = ph + spl + tot
    
    return {
        "total_intake": intake,
        "total_kea_seats": kea,
        "snq_5pct": snq,
        "over_above_5pct": snq,
        "kea_ph": ph,
        "kea_spl": spl,
        "kea_hk": hk,
        "kea_rk": rk,
        "kea_tot": tot,
        "cat2_seats": comedk,
        "cat3_seats": mgmt
    }

def parse_2026_pdf():
    colleges_2025 = load_2025_metadata()
    cutoffs_2026 = load_existing_2026_cutoffs()
    
    reader = pypdf.PdfReader(PDF_PATH)
    print(f"Total Pages to parse: {len(reader.pages)}")
    
    completed_colleges = {}
    pending_colleges = []
    current_annexure = "A"
    
    ANNEXURE_COLUMNS = {
        "A": 8, "B": 9, "C": 10, "D": 10, "M": 8, "O": 7, "P": 7, "Z": 8
    }
    
    ANNEXURE_TYPES = {
        "A": "Government Engineering Colleges/VTU Constitutent Colleges",
        "B": "Seats in Aided Courses of Aided Engineering Colleges",
        "C": "Private Unaided Engineering Colleges",
        "D": "Private Unaided Minority Engineering Colleges",
        "M": "Seats for Government Courses in Public Universities",
        "O": "Private Universities",
        "P": "Deemed Universities",
        "Z": "Government Colleges with Higher Fees"
    }

    # Define all indicators for college headers (excluding technology to avoid false matching course names)
    indicators = [
        "college", "university", "institute", "school", "academy", "constituent", "vtu", "cpgs", 
        "univesity", "technolory", "polyptechnic", "polytechnic", "unmrsity", "campus",
        "cotlege", "collegc", "tjniversity", "tiniversity", "tintversity", "fntversity", 
        "mlnstitute", "lnstitute", "tnstitute", "intitute", "institutc", "lnstitut",
        "institutute", "lnstitutions", "institutions"
    ]

    pending_course_prefix = None
    
    for page_num in range(3, 132): # Pages 3 to 131
        page = reader.pages[page_num - 1]
        text = page.extract_text() or ""
        if page_num == 11:
            text = text.replace("iz\nI\nCOMPUTER SCIENCE AND ENGINEERING\n(CYBER SECURITY)", "2 COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)")
        elif page_num == 19:
            text = text.replace("2 COMPUTER SCIENCE AND DESIGN 60 I 0 2 26 l8 15 3", "2 COMPUTER SCIENCE AND DESIGN 60 27 1 0 2 24 26 18 15 3")
            text = text.replace("),20", "120")
        elif page_num == 24:
            text = text.replace("30 13 I 0 I 1l l2 9 8 I I", "30 13 1 0 1 11 12 9 8")
        elif page_num == 28:
            text = text.replace("7 ELECTRONICS ENGINEEzuNG(VLSI\nDESIGN & TECHNOLOGY)\n60 )1\n1 0 2 24 26 l8 15 3", "7 ELECTRONICS ENGINEEzuNG(VLSI DESIGN & TECHNOLOGY) 60 27 1 0 2 24 26 l8 15 3")
            text = text.replace("60 I 0 2 26 18 l5 3", "60 27 I 0 2 24 26 18 l5 3")
        elif page_num == 32:
            text = text.replace("30 14 1 0 9 4 13 9 7 2 I", "30 14 1 0 9 4 13 9 7 2")
        elif page_num == 46:
            text = text.replace("6 ELECTRONICS AND COMMI,JMCATION\nENGG\n60 27 I 0\n,)\n24 26 18 l5 3", "6 ELECTRONICS AND COMMI,JMCATION ENGG 60 27 1 0 2 24 26 18 15 3")
        elif page_num == 48:
            text = text.replace("90 40 2 I 26 11 37 27 /) 4", "90 40 2 1 26 11 37 27 23 4")
        elif page_num == 52:
            text = text.replace("90 4t\n,)\n1 J 35 38 2't 22 4", "90 4t 1 J 35 38 2't 22 4")
            text = text.replace("120 54 J 1 4 46 50 Jt) 30 6", "120 54 J 1 4 46 50 36 30 6")
        elif page_num == 67:
            text = text.replace("60 )1 2 0 2 23 25 l8 l5 3", "60 27 2 0 2 23 25 l8 l5 3")
        elif page_num == 73:
            text = text.replace("60 )1 I 0 2 24 26 18 15 3", "60 27 I 0 2 24 26 18 15 3")
        elif page_num == 81:
            text = text.replace("60 )1 I 0 2 24 26 l8 l5 J", "60 27 I 0 2 24 26 l8 l5 J")
        elif page_num == 95:
            text = text.replace("60 )1 I 0 2 24 26 18 l5 3", "60 27 I 0 2 24 26 18 l5 3")
            text = text.replace("60 27 ) 1 2 22 24 18 l5 J", "60 27 2 1 2 22 24 18 l5 J")
        elif page_num == 100:
            text = text.replace("ANNEXT,RE : C", "ANNEXT,RE : D")
            text = text.replace("60 24 I 0 2 21 z5 18 18 J", "60 24 1 0 2 21 23 18 18 3")
        elif page_num == 101:
            text = text.replace("30 1) 1 0 I l0 11 9 9 2", "30 12 1 0 1 10 11 9 9 2")
        elif page_num == 102:
            text = text.replace("60 :+ 1 I l5 7 22 18 l8 )", "60 24 1 1 15 7 22 18 18 3")
        elif page_num == 106:
            text = text.replace("60 1 0 2 2l Z5 18 t8 J", "60 24 1 0 2 21 23 18 18 3")
        elif page_num == 107:
            text = text.replace("3 BIO-TECHNOLOGY 60 an\n1 0 2 2l 23 l8 18 J", "3 BIO-TECHNOLOGY 60 24 1 0 2 21 23 18 18 3")
        elif page_num == 110:
            text = text.replace("60 24 I 0 2 2l z5", "60 24 1 0 2 21 23")
        elif page_num == 111:
            text = text.replace("3 AMITY TINIVERSITY", "3 AMITY UNIVERSITY")
            text = text.replace("60 a/\n1 0 2 2t 23", "60 24 1 0 2 21 23")
            text = text.replace("60 AA\n1 0 2 2t 23", "60 24 1 0 2 21 23")
            text = text.replace("r20 48 J I 3 41. Mi", "120 48 2 1 3 42 45")
        elif page_num == 115:
            header_str = "l0 K L E Technological U1r-v_elltyaBelgaum Campus (Formerly KLE Dr M.S.Sheshagiri College of Engineering and Technology)\nAddress : UDYAMBAGH,BELGALTI4"
            text = text.replace(header_str, "")
            insert_after = "lns Total 960 384 19 2 29 334 363"
            text = text.replace(insert_after, insert_after + "\n" + header_str)
        elif page_num == 116:
            text = text.replace("11 Khaja Bandanawaz Universify", "11 Khaja Bandanawaz University")
            text = text.replace("240 96 5 1 63 27 e0 \nI", "240 96 5 1 63 27 90")
        elif page_num == 118:
            text = text.replace("120 288 l5 1 22 250 272", "720 288 15 1 22 250 272")
        elif page_num == 119:
            text = text.replace("60 24 I 0 2 21 25", "60 24 1 0 2 21 23")
        elif page_num == 120:
            text = text.replace("18 RAT TECIINOLOGICAL T]NTVERSTTY", "18 RAI TECHNOLOGICAL UNIVERSITY")
        elif page_num == 122:
            text = text.replace("21 RV University\nAddress : POLT NO 46,47,60,610P,KIADB INDUSTRTAL AREA5 NANJANAGUDU", "21 RV University Nanjanagudu\nAddress : POLT NO 46,47,60,610P,KIADB INDUSTRTAL AREA5 NANJANAGUDU")
            text = text.replace("21 RV University\nAddress : R.V. VIDYANIKETAN POST, MYSORE ROAD", "21 RV University Bengaluru\nAddress : R.V. VIDYANIKETAN POST, MYSORE ROAD")
        elif page_num == 123:
            text = text.replace("60 .A\n1 0 2 2t 23", "60 24 1 0 2 21 23")
            text = text.replace("2640 I 0s6", "2640 1056")
            header = "24 Sharanbasava University (Exclusively for Women) (Formerly Goduati trngineering College For Women)\nAddress : SFIARNBASVESHWARA INSTITUTIoNS CAMPUS . KALABURAGI ( GULBARGA) -585103 .I(anNafara"
            text = text.replace(header, "")
            text = text.replace("Ins Total 40 20 I I 1 t7 18", "Ins Total 40 20 I I 1 t7 18\n" + header)
        elif page_num == 125:
            text = text.replace("60 24 I 0 2 21 2.5", "60 24 1 0 2 21 23")
        elif page_num == 128:
            text = text.replace("60 1 0 2 2l z5", "60 24 1 0 2 21 23")
        elif page_num == 130:
            text = text.replace("30 30 I 0 J 26 29 0", "30 30 1 0 3 26 29 0")
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            line = line.replace(']', 'I').replace('[', 'I')
            # Clean known OCR merges and noises
            line = line.replace("'>A", "27")
            line = line.replace("J(,l", "2 30")
                
            # 1. Match annexure change FIRST, before filtering lines
            m_ann = re.search(r'(?:ANNEX|AI\\NEX|AI\\I\\IEX|A\\I\\IEX|A\\\\I\\\\IEX|A/\\I/\\IEX)[A-Za-z0-9\].\[\s\\/]*:\s*([A-Za-z0-9]+)', line, re.IGNORECASE)
            if m_ann:
                ann_val = m_ann.group(1).upper()
                if ann_val == "III":
                    ann_val = "M"
                if ann_val in ANNEXURE_COLUMNS:
                    current_annexure = ann_val
                continue
                
            # 2. Filter out page subtitles, headers, and footer signature blocks
            if any(x in line.lower() for x in ["seats in", "government notification", "detailed matrix", "new courses", "under secretary"]):
                continue
                
            # Preprocess line to clean OCR artifacts
            # 1. Strip leading non-alphanumeric junk characters (like - in -1l)
            line_proc = re.sub(r'^[^a-zA-Z0-9\s]+', '', line)
            
            # 2. Merge spaced serial numbers (like "I l0" to "Il0")
            tokens_temp = line_proc.split()
            if len(tokens_temp) >= 2 and sum(1 for t in tokens_temp if is_garbled_number(t)) < 5:
                def is_digit_like(s):
                    return all(c in "0123456789IlioO" for c in s)
                if is_digit_like(tokens_temp[0]) and is_digit_like(tokens_temp[1]):
                    if len(tokens_temp) >= 3 and is_digit_like(tokens_temp[2]):
                        merged = tokens_temp[0] + tokens_temp[1] + tokens_temp[2]
                        line_proc = merged + " " + " ".join(tokens_temp[3:])
                    else:
                        merged = tokens_temp[0] + tokens_temp[1]
                        line_proc = merged + " " + " ".join(tokens_temp[2:])
            
            # 3. Check num_count before stripping trailing single-letter junk
            tokens_temp = line_proc.split()
            num_count_temp = sum(1 for t in reversed(tokens_temp) if is_garbled_number(t))
            if num_count_temp < 5:
                line_proc = re.sub(r'\s+(!?[a-zA-Z]!?)\s*$', '', line_proc)
                
            # 4. Split glued prefix and name (e.g. 62HiraSugar -> 62 HiraSugar)
            line_proc = re.sub(r'^(\d+)([A-Za-z])', r'\1 \2', line_proc)
            line_proc = re.sub(r'^([Ee]\d+)([A-Za-z])', r'\1 \2', line_proc)
            line_proc = line_proc.replace(']', 'I').replace('[', 'I')
            # Merge split total seats (e.g. 'I lJ' -> 'IlJ')
            line_proc = line_proc.replace("I lJ", "IlJ").replace("I 1J", "I1J").replace("I 1j", "I1j")
            
            # 5. Address check FIRST to prevent address lines from being matched as course rows
            if line_proc.startswith("Address") or line_proc.startswith("AddTess") or line_proc.startswith("Addless") or line_proc.startswith("Addess") or line_proc.startswith("Addrs"):
                if pending_colleges:
                    pending_colleges[0]["address"] = line.replace("Address :", "").replace("AddTess :", "").replace("Addless :", "").strip()
                pending_course_prefix = None
                continue
                
            tokens = line_proc.split()
            
            num_count = 0
            for t in reversed(tokens):
                if is_garbled_number(t):
                    num_count += 1
                else:
                    break
            
            expected_n = ANNEXURE_COLUMNS.get(current_annexure, 10)
            
            if num_count >= 5:
                seat_tokens = tokens[-num_count:]
                name_tokens = tokens[:-num_count]
                
                # Check for total row with high OCR tolerance
                is_total_row = False
                if name_tokens:
                    name_lower_joined = " ".join(name_tokens).lower()
                    if any(x in name_lower_joined for x in ["ins", "total", "tot", "lns", "t0t"]):
                        is_total_row = True
                        
                if is_total_row:
                    if pending_colleges:
                        col = pending_colleges.pop(0)
                        completed_colleges[col["kea_code"]] = col
                    pending_course_prefix = None
                    continue
                
                is_hk_college = False
                col_code = None
                if pending_colleges:
                    is_hk_college = pending_colleges[0].get("district") in HK_DISTRICTS
                    col_code = pending_colleges[0]["kea_code"]
                    
                intake = clean_ocr_number(seat_tokens[0])
                seats = [clean_ocr_number(x) for x in seat_tokens]
                seats = align_seat_tokens(current_annexure, intake, seats, expected_n, is_hk_college, col_code)
                
                if len(seats) < expected_n:
                    seats += [0] * (expected_n - len(seats))
                elif len(seats) > expected_n:
                    seats = seats[-expected_n:]
                    
                parsed_seats = {
                    "total_kea_seats": seats[1],
                    "kea_ph": seats[2],
                    "kea_spl": seats[3],
                    "kea_hk": seats[4],
                    "kea_rk": seats[5],
                    "kea_tot": seats[6],
                    "cat2_seats": 0,
                    "cat3_seats": 0,
                    "snq_5pct": 0
                }
                
                if current_annexure in ["A", "M", "Z"]:
                    parsed_seats["snq_5pct"] = seats[7]
                elif current_annexure == "B":
                    parsed_seats["cat3_seats"] = seats[7]
                    parsed_seats["snq_5pct"] = seats[8]
                elif current_annexure in ["C", "D"]:
                    parsed_seats["cat2_seats"] = seats[7]
                    parsed_seats["cat3_seats"] = seats[8]
                    parsed_seats["snq_5pct"] = seats[9]
                
                if pending_course_prefix:
                    sl_no = pending_course_prefix[0]
                    prefix_name = pending_course_prefix[1]
                    course_name = prefix_name + " " + " ".join(name_tokens)
                    pending_course_prefix = None
                else:
                    if name_tokens and is_valid_course_prefix(name_tokens[0]):
                        sl_no = name_tokens[0]
                        course_name = " ".join(name_tokens[1:])
                    else:
                        sl_no = ""
                        course_name = " ".join(name_tokens)
                
                course_name = clean_course_name(course_name)
                intake = seats[0]
                
                if not pending_colleges and page_num == 91:
                    # Headerless college E033 (Sri Taralabalu) anomaly handler
                    matched = colleges_2025.get("sritaralabalujagadgururanebennur")
                    if matched:
                        new_col = {
                            "college_number": matched["college_number"],
                            "kea_code": matched["kea_code"],
                            "college_name": matched["college_name"],
                            "address": matched.get("address", ""),
                            "annexure": current_annexure,
                            "college_type": ANNEXURE_TYPES[current_annexure],
                            "district": matched.get("district", "Unknown"),
                            "courses": [],
                            "established": matched.get("established"),
                            "nirf_rank": matched.get("nirf_rank"),
                            "naac_grade": matched.get("naac_grade"),
                            "nba_accredited": matched.get("nba_accredited"),
                            "placements": matched.get("placements") or {},
                            "hostel_details": matched.get("hostel_details") or {},
                            "campus_life": matched.get("campus_life") or {},
                            "location_details": matched.get("location_details") or {}
                        }
                        pending_colleges.append(new_col)
                        print(f"Headerless college anomaly resolved: Added {matched['kea_code']} to pending on page {page_num}")
                
                if pending_colleges:
                    active_col = pending_colleges[0]
                    dist = active_col.get("district", "Unknown")
                    kea_code = active_col.get("kea_code")
                    clean_seats = sanitize_course_seats(current_annexure, dist, intake, parsed_seats, kea_code, course_name)
                    
                    cutoff_data = cutoffs_2026.get((kea_code, course_name)) or {
                        "round1_cutoff": {},
                        "round2_cutoff": {},
                        "round3_cutoff": {},
                        "mock_round1_cutoff": {}
                    }
                    
                    course_dict = {
                        "course_name": course_name,
                        "annexure": current_annexure,
                        **clean_seats,
                        **cutoff_data
                    }
                    existing_course = next((c for c in active_col["courses"] if c["course_name"] == course_name), None)
                    if existing_course:
                        existing_course["total_intake"] += course_dict["total_intake"]
                        existing_course["total_kea_seats"] += course_dict["total_kea_seats"]
                        existing_course["kea_ph"] += course_dict["kea_ph"]
                        existing_course["kea_spl"] += course_dict["kea_spl"]
                        existing_course["kea_hk"] += course_dict["kea_hk"]
                        existing_course["kea_rk"] += course_dict["kea_rk"]
                        existing_course["kea_tot"] += course_dict["kea_tot"]
                        existing_course["cat2_seats"] += course_dict["cat2_seats"]
                        existing_course["cat3_seats"] += course_dict["cat3_seats"]
                        existing_course["snq_5pct"] += course_dict["snq_5pct"]
                    else:
                        active_col["courses"].append(course_dict)
            else:
                header_triggers_word = {"intake", "kea", "seats", "total", "si.n", "hkrk", "hk-rk", "snq", "come", "dk", "mgmt", "above"}
                header_triggers_sub = {"course name", "cat-", "cat.", "mng/", "over &"}
                line_words = set(line.lower().split())
                is_header = False
                for trigger in header_triggers_word:
                    if trigger in line_words:
                        is_header = True
                        break
                if not is_header:
                    for trigger in header_triggers_sub:
                        if trigger in line.lower():
                            is_header = True
                            break
                if is_header:
                    pending_course_prefix = None
                    continue

                m_college = re.match(r'^([A-Za-z0-9]+)\s+([A-Za-z].*)$', line_proc)
                if not m_college:
                    m_college = re.match(r'^(\d+)([A-Za-z].*)$', line_proc)
                is_college = False
                matched = None
                
                if m_college:
                    g1 = m_college.group(1)
                    g2 = m_college.group(2)
                    g1_clean = clean_ocr_serial(g1)
                    if g1_clean.isdigit():
                        code = g1_clean
                        col_name = g2
                    else:
                        m_split = re.match(r'^(\d+)([A-Za-z].*)$', g1)
                        if m_split:
                            code = m_split.group(1)
                            col_name = (m_split.group(2) + " " + g2).strip()
                        else:
                            code = g1
                            col_name = g2
                        col_name = standardize_college_name(col_name)
                        
                    if code.upper() not in {"SI", "KEA", "PAGE", "ANNEX", "TOTAL", "SEATS", "NAME", "SL", "NO"} and len(code) <= 4:
                        is_college = any(ind in col_name.lower() for ind in indicators) and not any(cw in col_name.lower() for cw in ["b tech", "btech", "b.tech", "m tech", "mtech", "m.tech"])
                        matched = match_college(col_name, current_annexure, colleges_2025)
                        if matched and not any(cw in col_name.lower() for cw in ["b tech", "btech", "b.tech", "m tech", "mtech", "m.tech"]):
                            is_college = True

                if is_college:
                    # Safety net: Pop any pending colleges that already have parsed courses
                    while pending_colleges and len(pending_colleges[0]["courses"]) > 0:
                        col = pending_colleges.pop(0)
                        completed_colleges[col["kea_code"]] = col
                        
                    if matched:
                        kea_code = matched["kea_code"]
                        if kea_code in completed_colleges:
                            col = completed_colleges[kea_code]
                            if col not in pending_colleges:
                                pending_colleges.append(col)
                                del completed_colleges[kea_code]
                        elif not any(c["kea_code"] == kea_code for c in pending_colleges):
                            new_col = {
                                "college_number": int(code) if code.isdigit() else matched["college_number"],
                                "kea_code": kea_code,
                                "college_name": matched["college_name"],
                                "address": matched.get("address", ""),
                                "annexure": current_annexure,
                                "college_type": ANNEXURE_TYPES[current_annexure],
                                "district": matched.get("district", "Unknown"),
                                "courses": [],
                                "established": matched.get("established"),
                                "nirf_rank": matched.get("nirf_rank"),
                                "naac_grade": matched.get("naac_grade"),
                                "nba_accredited": matched.get("nba_accredited"),
                                "placements": matched.get("placements") or {},
                                "hostel_details": matched.get("hostel_details") or {},
                                "campus_life": matched.get("campus_life") or {},
                                "location_details": matched.get("location_details") or {}
                            }
                            pending_colleges.append(new_col)
                    else:
                        print(f"Creating fresh college (unmatched): {col_name}")
                        kea_code = "E" + str(len(completed_colleges) + len(pending_colleges) + 500).zfill(3)
                        new_col = {
                            "college_number": len(completed_colleges) + len(pending_colleges) + 500,
                            "kea_code": kea_code,
                            "college_name": col_name,
                            "address": "",
                            "annexure": current_annexure,
                            "college_type": ANNEXURE_TYPES[current_annexure],
                            "district": "Unknown",
                            "courses": []
                        }
                        pending_colleges.append(new_col)
                    pending_course_prefix = None
                else:
                    # Accumulate course line
                    if not any(trigger in line.lower() for trigger in ["annexure", "government notification", "unaided courses", "page", "address :", "addtess :"]):
                        if pending_course_prefix:
                            pending_course_prefix = (pending_course_prefix[0], pending_course_prefix[1] + " " + line)
                        else:
                            m_sl = re.match(r'^(\d+)\s+(.*)$', line)
                            if m_sl:
                                pending_course_prefix = (m_sl.group(1), m_sl.group(2))
                            else:
                                pending_course_prefix = ("", line)

    while pending_colleges:
        col = pending_colleges.pop(0)
        completed_colleges[col["kea_code"]] = col
        
    final_colleges = list(completed_colleges.values())
    final_colleges = [col for col in final_colleges if not any(arch in col["college_name"].lower() for arch in ["architecture", "planning", "b.arch", "b arch", "b.plan", "b plan"])]
    for col in final_colleges:
        col["total_intake"] = sum(c["total_intake"] for c in col["courses"])
        col["total_kea_seats"] = sum(c["total_kea_seats"] for c in col["courses"])
        
    return final_colleges

def main():
    print("Starting 2026 Seat Matrix PDF Parser...")
    colleges = parse_2026_pdf()
    print(f"\nParsed {len(colleges)} colleges successfully!")
    
    districts = sorted(list(set(c["district"] for c in colleges if c.get("district"))))
    all_courses = sorted(list(set(cr["course_name"] for c in colleges for cr in c["courses"])))
    
    total_seats = sum(c["total_intake"] for c in colleges)
    total_kea = sum(c["total_kea_seats"] for c in colleges)
    
    print(f"Total seats: {total_seats} | KEA seats: {total_kea}")
    
    output_data = {
        "metadata": {
            "year": 2026,
            "document": "ED 101 TEC 2026",
            "date": "29-06-2026"
        },
        "colleges": colleges,
        "all_courses": all_courses,
        "districts": districts,
        "stats": {
            "total_colleges": len(colleges),
            "total_seats": total_seats,
            "total_kea_seats": total_kea
        }
    }
    
    with open(OUTPUT_2026_JSON, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Saved output to {OUTPUT_2026_JSON}")
    
    with open(OUTPUT_BASELINE_JSON, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Saved output to {OUTPUT_BASELINE_JSON}")

if __name__ == "__main__":
    main()
