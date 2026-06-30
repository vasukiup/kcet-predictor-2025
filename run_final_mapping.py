import json
import re
import sys
import difflib

sys.stdout.reconfigure(encoding='utf-8')

from standardize_course_names import standardize_single_name, MANUAL_OVERRIDE_MAP
from merge_zero_intake_duplicates import courses_are_compatible

# Aided/Unaided split overrides and other exact overrides
MANUAL_OVERRIDES = {
    # Sapthagiri
    "sapthagiri nps university": "E108",
    "sapthagiri nps univeristy": "E108",
    
    # Architecture schools (no engineering cutoffs)
    "sir m v school of architecture,hunasamaranahalli, bangalore": None,
    "school of planning and architecture, university of mysore": None,
    "school of planning and architchure, university of mysore": None,
    "sjb school of achitecture & planning, uthrahalli road, kengeri, bangalore": None,
    "sjb school of architecture & planning, uthrahalli road, kengeri, bangalore": None,
    
    # Tumkur
    "sri siddhartha school of engineering, tumkur": "E081",
    "sri siddhartha institute of technology": "E017",
    
    # PES
    "pes university": "E009",
    "pes university (electronic city campus)": "E141",
    "pes university(electronic city campus)": "E141",
    
    # SJB
    "s.j b. institute of technology, bangalore (autonomous)": "E115",
    
    # Mysore
    "university of mysuru": "E283",
    "visvesvaraya technological university, vtu, cpgs, mysuru": "E290",
    "visvesvaraya technological university,vtu,cpgs,mysuru.": "E290",
    "cauvery college of engineering": "E314",
    "mysore college of engineering and management,mysore": "E252",
}

# Aided/Unaided splits based on name and Annexure
AIDED_UNITS = {
    "b m s college of engineering, basavanagudi, bangalore (autonomous)": {
        "B": "E003",
        "C": "E048",
        "E": "E048"
    },
    "b v v sangha's basaveshwara engineering college, bagalkote (autonomous)": {
        "B": "E031",
        "C": "E049",
        "E": "E049"
    },
    "b v v sangha`s basaveshwara engineering college , bagalkote (autonomous)": {
        "B": "E031",
        "C": "E049",
        "E": "E049"
    },
    "dr. ambedkar institute of technology, bangalore (autonomous)": {
        "B": "E004",
        "C": "E060",
        "E": "E060"
    },
    "dr. ambedkar institute of technology, bangalore(autonomous)": {
        "B": "E004",
        "C": "E060",
        "E": "E060"
    },
    "malnad college of engineering, hassan (autonomous)": {
        "B": "E024",
        "C": "E047",
        "E": "E047"
    },
    "malnad college of engineering, hassan(autonomous)": {
        "B": "E024",
        "C": "E047",
        "E": "E047"
    },
    "p d a college of engineering, gulbarga (autonomous)": {
        "B": "E041",
        "C": "E059",
        "E": "E059"
    },
    "p d a college of engineering, gulbarga(autonomous)": {
        "B": "E041",
        "C": "E059",
        "E": "E059"
    },
    "p e s college of engineering, mandya (autonomous)": {
        "B": "E023",
        "C": "E058",
        "E": "E058"
    },
    "p e s college of engineering, mandya(autonomous)": {
        "B": "E023",
        "C": "E058",
        "E": "E058"
    },
    "sri jayachamarajendra college of engineering (constituent college of jss science & technology university), Mysore": {
        "B": "E021",
        "C": "E284",
        "E": "E284"
    },
    "sri jayachamarajendra college of engineering (constituent college of jss science & technology university), mysore": {
        "B": "E021",
        "C": "E284",
        "E": "E284"
    },
    "sri jayachamarajendra college of engineering(constituent college of jss science & technology university), Mysore": {
        "B": "E021",
        "C": "E284",
        "E": "E284"
    },
    "sri jayachamarajendra college of engineering(constituent college of jss science & technology university), mysore": {
        "B": "E021",
        "C": "E284",
        "E": "E284"
    },
    "the national institute of engineering, Mysore (autonomous)": {
        "B": "E022",
        "C": "E056",
        "E": "E056"
    },
    "the national institute of engineering, mysore (autonomous)": {
        "B": "E022",
        "C": "E056",
        "E": "E056"
    },
    "the national institute of engineering, Mysore(autonomous)": {
        "B": "E022",
        "C": "E056",
        "E": "E056"
    },
    "the national institute of engineering, mysore(autonomous)": {
        "B": "E022",
        "C": "E056",
        "E": "E056"
    },
    "university b.d.t college of engineering, davanagere": {
        "A": "E061",
        "Z": "E066",
        "E": "E061"
    }
}

def clean_name(name):
    n = name.lower()
    n = re.sub(r'[^a-z0-9]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    n = n.replace('engineering', 'engg')
    n = n.replace('technology', 'tech')
    n = n.replace('autonomous', '')
    n = n.replace('constituent college of vtu', 'vtu')
    n = n.replace('university of visvesvaraya college of engg', 'uvce')
    n = n.replace('univesity of visvesvaraya college of engg', 'uvce')
    n = n.replace('university visvesvaraya college of engg', 'uvce')
    return n.strip()

GENERIC_WORDS = {
    'government', 'engg', 'college', 'technology', 'tech', 'institute', 
    'of', 'and', 'management', 'private', 'aided', 'unaided', 'autonomous', 
    'constituent', 'vtu', 'university', 'school', 'academy', 'technical', 
    'education', 'society', 'societys', 'societies', 'group', 'institutions', 
    'institution', 'cpgs', 'cpgs.', 'state', 'public', 'trust', 'trusts',
    'national', 'indian', 'regional', 'post', 'box', 'no', 'road', 'street',
    'campus', 'city', 'district', 'town', 'village',
    'bangalore', 'bengaluru', 'mysore', 'mysuru', 'mangalore', 'mangaluru', 
    'belgaum', 'belagavi'
}

def get_core_keywords(name):
    clean = clean_name(name)
    words = set(clean.split())
    core = words - GENERIC_WORDS
    core = {w for w in core if re.match(r'^[a-z0-9]+$', w)}
    return core

def run_mapping():
    with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
        sm_data = json.load(f)
        
    with open("round1_cutoffs.json", "r", encoding="utf-8") as f:
        r1_cutoff = json.load(f)
        
    with open("round2_cutoffs.json", "r", encoding="utf-8") as f:
        r2_cutoff = json.load(f)

    with open("round3_cutoffs.json", "r", encoding="utf-8") as f:
        r3_cutoff = json.load(f)
        
    # Load unified course mapping
    with open("course_standardization_map.json", "r", encoding="utf-8") as f:
        std_map = json.load(f)
        
    # Helper to standardise cutoff dictionaries
    def standardize_cutoff_dict(cutoff_dict):
        std_cutoff = {}
        for code, info in cutoff_dict.items():
            std_courses = {}
            for raw_cname, data in info["courses"].items():
                matched_override = None
                for raw_k, clean_v in MANUAL_OVERRIDE_MAP.items():
                    if raw_cname.upper().strip() == raw_k.upper().strip():
                        matched_override = clean_v
                        break
                
                if matched_override:
                    std_cname = matched_override
                elif raw_cname in std_map:
                    std_cname = standardize_single_name(std_map[raw_cname])
                else:
                    std_cname = standardize_single_name(raw_cname)
                std_courses[std_cname] = data
            std_cutoff[code] = {
                "college_name": info["college_name"],
                "courses": std_courses
            }
        return std_cutoff

    print("Standardizing cutoff course names in memory...")
    r1_cutoff = standardize_cutoff_dict(r1_cutoff)
    r2_cutoff = standardize_cutoff_dict(r2_cutoff)
    r3_cutoff = standardize_cutoff_dict(r3_cutoff)
        
    # Pre-clean cutoff data for college matching
    cutoff_cleaned = {}
    for code, info in r1_cutoff.items():
        cutoff_cleaned[code] = {
            'name': info['college_name'],
            'clean': clean_name(info['college_name']),
            'core': get_core_keywords(info['college_name']),
            'courses': set(info['courses'].keys())
        }
        
    mapped_count = 0
    skipped_count = 0
    
    for sm_col in sm_data["colleges"]:
        name = sm_col["college_name"]
        name_lower = name.lower().strip()
        annex = sm_col.get("annexure", "C")
        
        best_match = sm_col.get("kea_code")
        if best_match:
            pass
        # 1. Check Aided/Unaided Splits
        elif name_lower in AIDED_UNITS:
            best_match = AIDED_UNITS[name_lower].get(annex)
        # 2. Check Manual Overrides
        elif name_lower in MANUAL_OVERRIDES:
            best_match = MANUAL_OVERRIDES[name_lower]
        # 3. Dynamic Match
        else:
            sm_clean = clean_name(name)
            sm_core = get_core_keywords(name)
            sm_courses = set(c["course_name"] for c in sm_col["courses"])
            
            scored = []
            for code, info in cutoff_cleaned.items():
                if sm_core and info['core']:
                    intersect_words = sm_core & info['core']
                    if not intersect_words:
                        continue
                
                ratio = difflib.SequenceMatcher(None, sm_clean, info['clean']).ratio()
                intersect = len(sm_courses & info['courses'])
                overlap_score = len(sm_core & info['core'])
                scored.append((code, ratio, intersect, overlap_score))
                
            if scored:
                scored.sort(key=lambda x: (-x[3], -x[1], -x[2]))
                best_match = scored[0][0]
                
        if best_match is None:
            skipped_count += 1
            sm_col["kea_code"] = None
            for sm_course in sm_col["courses"]:
                sm_course["round1_cutoff"] = {}
                sm_course["round2_cutoff"] = {}
                sm_course["round3_cutoff"] = {}
            continue
            
        sm_col["kea_code"] = best_match
        mapped_count += 1
        
        # Map course cutoffs for all three rounds
        for sm_course in sm_col["courses"]:
            c_name = sm_course["course_name"]
            
            def get_cutoff_data(cutoff_dict, code, course_name):
                # 1. Determine codes to try (with E056 South Campus falling back to E178 North Campus for CS courses)
                codes_to_try = [code]
                if code == "E056":
                    codes_to_try.append("E178")
                
                # 2. Standardize target course name using same logic as cutoff standardizer
                std_cname = standardize_single_name(course_name)
                
                for c_code in codes_to_try:
                    if c_code not in cutoff_dict:
                        continue
                    
                    # 2.1 Try standardized lookup
                    if std_cname in cutoff_dict[c_code]["courses"]:
                        return cutoff_dict[c_code]["courses"][std_cname]
                    # 2.2 Try direct lookup
                    if course_name in cutoff_dict[c_code]["courses"]:
                        return cutoff_dict[c_code]["courses"][course_name]
                    # 2.3 Try compatible match fallback
                    for cut_cname, cut_data in cutoff_dict[c_code]["courses"].items():
                        if courses_are_compatible(course_name, cut_cname) or courses_are_compatible(std_cname, cut_cname):
                            return cut_data
                return {}
                
            sm_course["round1_cutoff"] = get_cutoff_data(r1_cutoff, best_match, c_name)
            sm_course["round2_cutoff"] = get_cutoff_data(r2_cutoff, best_match, c_name)
            sm_course["round3_cutoff"] = get_cutoff_data(r3_cutoff, best_match, c_name)
            
    print(f"Mapped {mapped_count} colleges successfully.")
    print(f"Skipped {skipped_count} colleges (Architecture/unmapped).")
    
    # Save the updated matrix
    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(sm_data, f, indent=2, ensure_ascii=False)
        
    print("Successfully rebuilt seat_matrix_data.json with correct mappings!")

if __name__ == "__main__":
    run_mapping()
