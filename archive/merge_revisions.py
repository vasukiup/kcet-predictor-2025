import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Load seat_matrix_data.json
with open("seat_matrix_data.json", encoding="utf-8") as f:
    db = json.load(f)

colleges = db["colleges"]

# Separate E and V colleges from the baseline colleges
baseline_colleges = [c for c in colleges if c["annexure"] not in ("E", "V")]
e_colleges = [c for c in colleges if c["annexure"] == "E"]
v_colleges = [c for c in colleges if c["annexure"] == "V"]

print(f"Loaded {len(baseline_colleges)} baseline colleges, {len(e_colleges)} E revisions, {len(v_colleges)} V revisions.")

def norm(name):
    n = name.upper()
    n = re.sub(r'\(AUTONOMOUS\)', '', n)
    n = re.sub(r'FORMERLY.*', '', n)
    n = re.sub(r'[^A-Z0-9]', '', n)
    return n

def course_matches(code, full_name):
    c = code.upper().strip()
    f = full_name.upper().strip()
    
    # Map abbreviation codes to baseline names
    if c == "CE" and "CIVIL" in f: return True
    if c == "CS" and "COMPUTER SCIENCE" in f: return True
    if c == "EC" and "ELECTRONICS" in f and "COMMUNICATION" in f: return True
    if c == "EE" and "ELECTRICAL" in f: return True
    if c == "ME" and "MECHANICAL" in f: return True
    if c == "IEM" and "INDUSTRIAL" in f and "MANAGEMENT" in f: return True
    if c == "IP" and "INDUSTRIAL" in f and "PRODUCTION" in f: return True
    if c == "PST" and "POLYMER" in f: return True
    if c == "EI" and ("INSTRUMENTATION" in f or "EI" in f): return True
    if c == "ENV" and "ENVIRONMENTAL" in f: return True
    
    # Fallback to normalized check
    n_c = norm(c)
    n_f = norm(f)
    return n_c in n_f or n_f in n_c

# Build a lookup of baseline colleges by normalized name
baseline_by_name = {}
for c in baseline_colleges:
    n = norm(c["college_name"])
    if n not in baseline_by_name:
        baseline_by_name[n] = []
    baseline_by_name[n].append(c)

# Manual overrides for E and V colleges that have name changes or specific target mapping
# Note: the keys MUST be normalized using the norm() function (which strips 'FORMERLY...')
MANUAL_MAPPINGS = {
    # Yenepoya is a new college in E, put it in C (Private Unaided)
    "YENEPOYAINSTITUTEOFTECHNOLOGYMANGALORE": ("C", "Yenepoya Institute Of Technology, Mangalore", "Private Unaided Colleges"),
    
    # AJ Institute
    "AJINSTITUTEOFENGINEERINGANDTECHNOLOGYKOTTARCHOWKIBOLOORVILLAGEMANGALORE": ("D", "A J Institute Of Engineering And Technology, Mangalore", "Private Unaided Minority Colleges"),
    
    # UVCE (target name has the suffix!)
    "UNIVESITYOFVISVESVARAYACOLLEGEOFENGINEERINGASTATEAUTONOMOUSPUBLICUNIVERSITYONIITMODEL": ("M", "University of Visvesvaraya College of Engineering (A State Autonomous Public University on IIT Model)", "Government Public University"),
    
    # KLE Belgaum (key is stripped of 'FORMERLY...')
    "KLETECHNOLOGICALUNIVERISTYBELGAUMCAMPUS": ("O", "K L E Technological University, Belgaum Campus (Formerly KLE Dr M.S. Sheshgiri College of Engineering)", "Private University"),
    
    # Sapthagiri
    "SAPTHAGIRINPSUNIVERISTY": ("O", "SAPTHAGIRI NPS UNIVERSITY", "Private University"),
    
    # School of Planning Mysore
    "SCHOOLOFPLANNINGANDARCHITCHUREUNIVERSITYOFMYSORE": ("O", "School of Planning and Architecture, University of Mysore", "Private University"),
    
    # GITAM Deemed University
    "GANDHIINSTITUTEOFTECHNOLOGYANDMANAGEMENTGITAMOFFCAMPUSBENGALURU": ("P", "GANDHI INSTITUTE OF TECHNOLOGY AND MANAGEMENT (GITAM) OFF CAMPUS BENGALURU", "Deemed University"),
    
    # SSIT Deemed University
    "SRISIDDHARTHAINSTITUTEOFTECHNOLOGY": ("P", "Sri Siddhartha Institute of Technology", "Deemed University"),
    
    # Alliance and Presidency Universities manual mapping (Consolidated revisions from Annexure V to Annexure O)
    "ALLIANCEUNIVERSITY": ("O", "ALLIANCE University", "Private University"),
    "PRESIDENCYUNIVERSITY": ("O", "PRESIDENCY University", "Private University")
}

def copy_special_seats(source_col, target_col, all_revisions=None):
    # Copies special seats fields from source_col's courses to target_col's courses.
    # Also appends any courses from source_col that only have special seats (intake=0) and don't exist in target_col.
    special_fields = ["sports", "ncc", "sct_guides", "defence", "k_defence", "ex_defence", "capf", "ai", "xcapf", "tot_special_seats"]
    
    target_course_map = {}
    for tc in target_col.get("courses", []):
        target_course_map[norm(tc["course_name"])] = tc
        
    for sc in source_col.get("courses", []):
        # Check if this source course has any special seats
        has_special = any(sc.get(f, 0) > 0 for f in special_fields)
        if not has_special:
            continue
            
        # Try to find matching course in target
        tc = target_course_map.get(norm(sc["course_name"]))
        if tc:
            # Copy fields
            for f in special_fields:
                if f in sc:
                    tc[f] = sc[f]
        else:
            # If not found, and it has special seats, check if another revision of the same college has it!
            is_offered_elsewhere = False
            if all_revisions:
                for r in all_revisions:
                    r_code = r.get("kea_code")
                    r_target = None
                    if r_code in KEA_CODE_TO_BASELINE:
                        r_target = KEA_CODE_TO_BASELINE[r_code]
                    else:
                        r_n = norm(r["college_name"])
                        if r_n in MANUAL_MAPPINGS:
                            r_target = (MANUAL_MAPPINGS[r_n][0], None)
                        elif r_n in baseline_by_name:
                            bcs = baseline_by_name[r_n]
                            if not (len(bcs) == 2 and {bc["annexure"] for bc in bcs} == {"B", "C"}):
                                r_target = (bcs[0]["annexure"], bcs[0]["college_number"])
                    
                    if r_target and target_col.get("college_number"):
                        if r_target[0] == target_col["annexure"] and r_target[1] == target_col["college_number"]:
                            # Check if this other revision has the course with positive intake
                            for rc in r.get("courses", []):
                                if norm(rc["course_name"]) == norm(sc["course_name"]) and rc.get("total_intake", 0) > 0:
                                    is_offered_elsewhere = True
                                    break
                    if is_offered_elsewhere:
                        break
                        
            if is_offered_elsewhere:
                print(f"  Skipping copy of special seat for '{sc['course_name']}' to '{target_col['college_name']}' ({target_col.get('kea_code')}) because another revision offers it.")
                continue

            # If not found, and it has special seats, append it to target courses
            # We copy the entire course but set intake/kea to 0 (since it doesn't exist in the revision)
            new_c = {
                "course_name": sc["course_name"],
                "total_intake": 0,
                "total_kea_seats": 0,
                "snq_5pct": 0, "kea_ph": 0, "kea_spl": 0, "kea_hk": 0, "kea_rk": 0, "kea_tot": 0,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 0,
            }
            for f in special_fields:
                if f in sc:
                    new_c[f] = sc[f]
            target_col["courses"].append(new_c)

merged_colleges = []
replaced_baseline_keys = set() # (annexure, college_number) of replaced baseline colleges

# Process E and V colleges
KEA_CODE_TO_BASELINE = {
    # BMS
    "E003": ("B", 1),
    "E048": ("C", 16),
    # Basaveshwara
    "E031": ("B", 2),
    "E049": ("C", 19),
    # Dr. Ambedkar
    "E004": ("B", 3),
    "E060": ("C", 44),
    # Malnad
    "E024": ("B", 4),
    "E047": ("C", 82),
    # SJCE
    "E021": ("B", 7),
    "E284": ("C", 128),
    # NIE
    "E022": ("B", 8),
    "E056": ("C", 137),
    # UBDT
    "E061": ("A", 19),
    "E066": ("Z", 2),
    # PDA
    "E041": ("B", 5),
    "E059": ("C", 92),
    # PES Mandya
    "E023": ("B", 6),
    "E058": ("C", 93),
    # Chintamani
    "E308": ("A", 1),
    "E309": ("Z", 1),
}

revisions = e_colleges + v_colleges
for rev in revisions:
    # 1. KEA code exact matching
    code = rev.get("kea_code")
    if code in KEA_CODE_TO_BASELINE:
        target_ann, target_num = KEA_CODE_TO_BASELINE[code]
        bc = next((c for c in baseline_colleges if c["annexure"] == target_ann and c["college_number"] == target_num), None)
        if bc:
            rev["annexure"] = target_ann
            rev["college_type"] = bc["college_type"]
            rev["college_number"] = bc["college_number"]
            
            # COPY SPECIAL SEATS!
            copy_special_seats(bc, rev, revisions)
                
            merged_colleges.append(rev)
            replaced_baseline_keys.add((target_ann, target_num))
            print(f"Mapped revised college '{rev['college_name']}' via KEA code '{code}' to [{target_ann}] #{target_num}")
            continue

    n = norm(rev["college_name"])
    
    # Check manual mappings first
    if n in MANUAL_MAPPINGS:
        target_ann, target_name, target_type = MANUAL_MAPPINGS[n]
        rev["annexure"] = target_ann
        rev["college_name"] = target_name
        rev["college_type"] = target_type
        
        # Mark all baseline colleges matching EITHER the V name or the target name as replaced!
        for name_key in (n, norm(target_name)):
            if name_key in baseline_by_name:
                for bc in baseline_by_name[name_key]:
                    replaced_baseline_keys.add((bc["annexure"], bc["college_number"]))
                    # COPY SPECIAL SEATS!
                    copy_special_seats(bc, rev, revisions)
                    print(f"Marked baseline college to replace: [{bc['annexure']}] #{bc['college_number']} {bc['college_name']}")
                    
        merged_colleges.append(rev)
        print(f"Mapped revised college '{rev['college_name']}' manually to Annexure {target_ann}")
        continue
        
    # Standard matching
    if n in baseline_by_name:
        bcs = baseline_by_name[n]
        
        # If the college exists in both B and C in baseline, split the revised courses!
        if len(bcs) == 2 and {bc["annexure"] for bc in bcs} == {"B", "C"}:
            b_bc = next(bc for bc in bcs if bc["annexure"] == "B")
            c_bc = next(bc for bc in bcs if bc["annexure"] == "C")
            
            # Create two separate college entries for the revision
            rev_b = json.loads(json.dumps(rev))
            rev_c = json.loads(json.dumps(rev))
            
            # Filter courses for B using course_matches
            rev_b["courses"] = [
                cr for cr in rev["courses"]
                if any(course_matches(cr["course_name"], b_cr["course_name"]) for b_cr in b_bc["courses"])
            ]
            rev_b["annexure"] = "B"
            rev_b["college_type"] = b_bc["college_type"]
            rev_b["college_number"] = b_bc["college_number"]
            rev_b["total_intake"] = sum(cr["total_intake"] for cr in rev_b["courses"])
            rev_b["total_kea_seats"] = sum(cr["total_kea_seats"] for cr in rev_b["courses"])
            
            # Filter courses for C (anything not mapped to B goes to C)
            b_mapped_names = {cr["course_name"] for cr in rev_b["courses"]}
            rev_c["courses"] = [
                cr for cr in rev["courses"]
                if cr["course_name"] not in b_mapped_names
            ]
            rev_c["annexure"] = "C"
            rev_c["college_type"] = c_bc["college_type"]
            rev_c["college_number"] = c_bc["college_number"]
            rev_c["total_intake"] = sum(cr["total_intake"] for cr in rev_c["courses"])
            rev_c["total_kea_seats"] = sum(cr["total_kea_seats"] for cr in rev_c["courses"])
            
            # COPY SPECIAL SEATS!
            copy_special_seats(b_bc, rev_b, revisions)
            copy_special_seats(c_bc, rev_c, revisions)
            
            merged_colleges.append(rev_b)
            merged_colleges.append(rev_c)
            
            replaced_baseline_keys.add(("B", b_bc["college_number"]))
            replaced_baseline_keys.add(("C", c_bc["college_number"]))
            print(f"Split revised college '{rev['college_name']}' into Aided (B) and Private (C) entries with {len(rev_b['courses'])} aided and {len(rev_c['courses'])} private courses")
            
        else:
            # Matches exactly one baseline college
            bc = bcs[0]
            rev["annexure"] = bc["annexure"]
            rev["college_type"] = bc["college_type"]
            rev["college_number"] = bc["college_number"]
            # COPY SPECIAL SEATS!
            copy_special_seats(bc, rev, revisions)
            merged_colleges.append(rev)
            replaced_baseline_keys.add((bc["annexure"], bc["college_number"]))
            print(f"Mapped revised college '{rev['college_name']}' to Annexure {bc['annexure']}")
    else:
        # No match found, keep as is
        merged_colleges.append(rev)
        print(f"WARNING: Revised college '{rev['college_name']}' had no baseline match!")

# Add all baseline colleges that were NOT replaced
for bc in baseline_colleges:
    key = (bc["annexure"], bc["college_number"])
    if key not in replaced_baseline_keys:
        merged_colleges.append(bc)
    else:
        print(f"Removed baseline college: [{bc['annexure']}] #{bc['college_number']} {bc['college_name']}")

# Save the merged colleges
db["colleges"] = merged_colleges

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("\nSaved merged data to seat_matrix_data.json")
