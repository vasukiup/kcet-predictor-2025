"""
KCET Seat Matrix Database Post-Processor
Automatically merges 0-intake course records (created due to name mismatches between baseline and special category sheets)
into their corresponding standard course records inside each college.
"""
import json
import re

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

def clean_course_name(name):
    n = name.lower()
    n = n.replace("sicence", "science")
    n = re.sub(r'^b\s*(\.?)\s*(tech|technology)\s+(in\s+)?', '', n)
    n = n.replace('&', 'and')
    n = re.sub(r'\bengg\b', 'engineering', n)
    n = re.sub(r'\btech\b', 'technology', n)
    n = re.sub(r'[^a-z0-9]', '', n)
    return n

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

def merge_zero_intake_duplicates():
    with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
        db = json.load(f)

    special_fields = ["sports", "ncc", "sct_guides", "defence", "k_defence", "ex_defence", "capf", "ai", "xcapf", "tot_special_seats"]
    merged_count = 0

    print("Post-processing: merging compatible 0-intake courses...")

    for col in db["colleges"]:
        courses = col.get("courses", [])
        
        # Separate 0-intake and positive-intake courses
        zero_courses = [co for co in courses if co.get("total_intake", 0) == 0]
        pos_courses = [co for co in courses if co.get("total_intake", 0) > 0]
        
        if not zero_courses or not pos_courses:
            continue
            
        to_remove = []
        for zc in zero_courses:
            # Find compatible positive-intake course
            match = None
            for pc in pos_courses:
                if courses_are_compatible(pc["course_name"], zc["course_name"]):
                    match = pc
                    break
            
            if match:
                # Merge zc special fields into match
                for f in special_fields:
                    if f in zc:
                        match[f] = match.get(f, 0) + zc[f]
                to_remove.append(zc)
                print(f"  [{col['annexure']}] {col['college_name']}: Merged '{zc['course_name']}' -> '{match['course_name']}'")
                merged_count += 1
                
        # Remove merged courses from college's list
        if to_remove:
            col["courses"] = [co for co in courses if co not in to_remove]

    # Save the updated database
    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"Post-processing Complete: merged {merged_count} duplicate 0-intake courses successfully.")

if __name__ == "__main__":
    merge_zero_intake_duplicates()
