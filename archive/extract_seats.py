import pdfplumber
import json
import re

PDF_PATH = "Seat_Matrix_05072025.pdf"

def detect_annexure(text):
    if "ANNEXURE : A" in text:
        return "A"
    elif "ANNEXURE : B" in text:
        return "B"
    elif "ANNEXURE : C" in text:
        return "C"
    elif "ANNEXURE : D" in text:
        return "D"
    elif "ANNEXURE : E" in text:
        return "E"
    return None

ANNEXURE_LABELS = {
    "A": "Government / VTU Constituent Colleges",
    "B": "Government Aided Private Colleges",
    "C": "Private Unaided Colleges",
    "D": "Private Unaided Minority Colleges",
    "E": "Detailed Matrix (New Courses/Intake)"
}

def parse_govt_college_page(text, current_annexure):
    """Parse Annexure A & B pages - Government colleges"""
    colleges = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    i = 0
    current_college = None
    
    while i < len(lines):
        line = lines[i]
        
        # Detect college header - number followed by college name
        m = re.match(r'^(\d+)\s+(.+)$', line)
        if m:
            num = m.group(1)
            name = m.group(2)
            # Check if next line is "Address :"
            if i + 1 < len(lines) and lines[i+1].startswith("Address"):
                if current_college:
                    colleges.append(current_college)
                address = lines[i+1].replace("Address :", "").strip()
                current_college = {
                    "college_number": int(num),
                    "college_name": name.strip(),
                    "address": address,
                    "annexure": current_annexure,
                    "college_type": ANNEXURE_LABELS.get(current_annexure, ""),
                    "courses": []
                }
                i += 2
                continue
        
        # Detect course rows - starts with a number, then course name, then seat numbers
        # Pattern: number course_name numbers...
        m2 = re.match(r'^(\d+)\s+([A-Z][A-Z\s&()/,\-]+?)\s+(\d+)\s+(\d+)', line)
        if m2 and current_college:
            course_num = m2.group(1)
            course_name = m2.group(2).strip()
            rest = line[m2.start(3):]
            nums = re.findall(r'\d+', rest)
            
            if len(nums) >= 2:
                total_intake = int(nums[0])
                total_kea = int(nums[1])
                
                course_entry = {
                    "course_name": course_name,
                    "total_intake": total_intake,
                    "total_kea_seats": total_kea,
                }
                
                # For annexure A (govt) - parse KEA PH SPL HK RK TOT Over
                if current_annexure in ["A", "B"] and len(nums) >= 8:
                    course_entry.update({
                        "snq_5pct": int(nums[2]) if len(nums) > 2 else 0,
                        "kea_ph": int(nums[3]) if len(nums) > 3 else 0,
                        "kea_spl": int(nums[4]) if len(nums) > 4 else 0,
                        "kea_hk": int(nums[5]) if len(nums) > 5 else 0,
                        "kea_rk": int(nums[6]) if len(nums) > 6 else 0,
                        "kea_tot": int(nums[7]) if len(nums) > 7 else 0,
                        "over_above_5pct": int(nums[8]) if len(nums) > 8 else 0,
                    })
                    course_entry["cat1_govt_pct"] = 100
                    course_entry["cat2_pct"] = 0
                    course_entry["cat3_pct"] = 0
                    course_entry["cat2_seats"] = 0
                    course_entry["cat3_seats"] = 0
                    
                # For annexure C (private unaided) - CAT1 45%, CAT2 30%, CAT3 25%
                elif current_annexure == "C" and len(nums) >= 10:
                    course_entry.update({
                        "snq_5pct": int(nums[2]) if len(nums) > 2 else 0,
                        "kea_ph": int(nums[3]) if len(nums) > 3 else 0,
                        "kea_spl": int(nums[4]) if len(nums) > 4 else 0,
                        "kea_hk": int(nums[5]) if len(nums) > 5 else 0,
                        "kea_rk": int(nums[6]) if len(nums) > 6 else 0,
                        "kea_tot": int(nums[7]) if len(nums) > 7 else 0,
                        "cat2_seats": int(nums[8]) if len(nums) > 8 else 0,
                        "cat3_seats": int(nums[9]) if len(nums) > 9 else 0,
                        "over_above_5pct": int(nums[10]) if len(nums) > 10 else 0,
                    })
                    course_entry["cat1_govt_pct"] = 45
                    course_entry["cat2_pct"] = 30
                    course_entry["cat3_pct"] = 25
                    
                # For annexure D (minority) - CAT1 40%, CAT2 30%, CAT3 30%
                elif current_annexure == "D" and len(nums) >= 10:
                    course_entry.update({
                        "snq_5pct": int(nums[2]) if len(nums) > 2 else 0,
                        "kea_ph": int(nums[3]) if len(nums) > 3 else 0,
                        "kea_spl": int(nums[4]) if len(nums) > 4 else 0,
                        "kea_hk": int(nums[5]) if len(nums) > 5 else 0,
                        "kea_rk": int(nums[6]) if len(nums) > 6 else 0,
                        "kea_tot": int(nums[7]) if len(nums) > 7 else 0,
                        "cat2_seats": int(nums[8]) if len(nums) > 8 else 0,
                        "cat3_seats": int(nums[9]) if len(nums) > 9 else 0,
                        "over_above_5pct": int(nums[10]) if len(nums) > 10 else 0,
                    })
                    course_entry["cat1_govt_pct"] = 40
                    course_entry["cat2_pct"] = 30
                    course_entry["cat3_pct"] = 30
                else:
                    course_entry.update({
                        "kea_ph": 0, "kea_spl": 0, "kea_hk": 0, "kea_rk": 0,
                        "kea_tot": 0, "cat2_seats": 0, "cat3_seats": 0,
                        "snq_5pct": 0, "over_above_5pct": 0,
                        "cat1_govt_pct": 100, "cat2_pct": 0, "cat3_pct": 0
                    })
                
                current_college["courses"].append(course_entry)
        
        # Detect Ins Total line to capture total
        if line.startswith("Ins Total") and current_college:
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                current_college["total_intake"] = int(nums[0])
                current_college["total_kea_seats"] = int(nums[1])
        
        i += 1
    
    if current_college:
        colleges.append(current_college)
    
    return colleges


def extract_district(address):
    """Try to extract district from address string"""
    address_upper = address.upper()
    districts = [
        "BANGALORE", "BENGALURU", "MYSORE", "MYSURU", "HUBLI", "DHARWAD",
        "BELGAUM", "BELAGAVI", "MANGALORE", "MANGALURU", "HASSAN", "SHIMOGA",
        "SHIVAMOGGA", "TUMKUR", "TUMAKURU", "BELLARY", "BALLARI", "GULBARGA",
        "KALABURAGI", "BIDAR", "RAICHUR", "KOPPAL", "GADAG", "HAVERI",
        "UTTARA KANNADA", "DAKSHINA KANNADA", "UDUPI", "CHIKMAGALUR",
        "CHIKKAMAGALURU", "KODAGU", "CHAMARAJANAGAR", "MANDYA", "KOLAR",
        "CHIKKABALLAPURA", "RAMANAGAR", "CHITRADURGA", "DAVANAGERE",
        "BAGALKOT", "BIJAPUR", "VIJAYAPURA", "YADGIR", "CHIKBALLAPURA"
    ]
    for d in districts:
        if d in address_upper:
            return d.title()
    return "Other"


def main():
    all_colleges = []
    current_annexure = None

    print("Starting PDF extraction...")
    
    with pdfplumber.open(PDF_PATH) as pdf:
        total = len(pdf.pages)
        print(f"Total pages: {total}")
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            
            # Detect annexure changes
            ann = detect_annexure(text)
            if ann and ann != "E":  # Skip E - it's detailed breakdown
                current_annexure = ann
            
            if current_annexure in ["A", "B", "C", "D"] and "ANNEXURE" in text:
                colleges = parse_govt_college_page(text, current_annexure)
                all_colleges.extend(colleges)
            
            if page_num % 50 == 0:
                print(f"  Processed page {page_num + 1}/{total}, colleges so far: {len(all_colleges)}")
    
    # Add district info
    for c in all_colleges:
        c["district"] = extract_district(c.get("address", ""))
    
    # Deduplicate colleges (same name + annexure)
    seen = {}
    deduped = []
    for c in all_colleges:
        key = (c["college_name"], c["annexure"])
        if key not in seen:
            seen[key] = True
            deduped.append(c)
        else:
            # Merge courses if already seen
            for existing in deduped:
                if (existing["college_name"], existing["annexure"]) == key:
                    existing_courses = {x["course_name"] for x in existing["courses"]}
                    for course in c["courses"]:
                        if course["course_name"] not in existing_courses:
                            existing["courses"].append(course)
                    break
    
    # Build summary stats
    all_courses = set()
    for c in deduped:
        for course in c["courses"]:
            all_courses.add(course["course_name"])
    
    output = {
        "metadata": {
            "notification": "ED 170 TEC 2025",
            "date": "05-07-2025",
            "total_colleges": len(deduped),
            "total_courses_offered": len(all_courses),
            "annexures": {
                "A": "Government / VTU Constituent Colleges (100% KEA)",
                "B": "Government Aided Private Colleges",
                "C": "Private Unaided Colleges (45% KEA / 30% COMEDK / 25% Mgmt)",
                "D": "Private Unaided Minority Colleges (40% KEA / 30% COMEDK / 30% Mgmt)"
            }
        },
        "colleges": deduped,
        "all_courses": sorted(list(all_courses))
    }
    
    output_path = "seat_matrix_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Extraction complete!")
    print(f"   Total colleges: {len(deduped)}")
    print(f"   Unique courses: {len(all_courses)}")
    print(f"   Output saved to: {output_path}")
    
    # Print annexure breakdown
    from collections import Counter
    ann_count = Counter(c["annexure"] for c in deduped)
    print("\n   Colleges by Annexure:")
    for ann, count in sorted(ann_count.items()):
        print(f"     Annexure {ann}: {count} colleges")
    
    # Sample
    print("\n   Sample colleges:")
    for c in deduped[:3]:
        print(f"     [{c['annexure']}] {c['college_name']} — {len(c['courses'])} courses")

if __name__ == "__main__":
    main()
