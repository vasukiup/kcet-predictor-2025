import pdfplumber
import re

def parse_college_courses(lines, annexure):
    course_blocks = []
    current_block = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip noise lines that are not courses or wrapped names
        if (not line
            or "ANNEXURE" in line
            or "ENGINEERING SEATS" in line
            or "GOVERNMENT NOTIFICATION" in line
            or "Seats in " in line
            or line.startswith("Sl.N")
            or line.startswith("Intake")
            or "SNQ" in line
            or "HK-RK" in line
            or "KRLMP" in line
            or "COMEDK" in line
            or re.match(r'^\d+$', line)       # bare page number
        ):
            i += 1
            continue
            
        m_start = re.match(r'^(\d+)\s+([A-Z].*)$', line)
        is_course_start = False
        if m_start:
            nums = re.findall(r'\d+', line)
            if len(nums) >= 3:
                is_course_start = True
                
        if is_course_start:
            if current_block:
                course_blocks.append(current_block)
            current_block = {
                "start_line": line,
                "wrapped_lines": []
            }
        elif current_block:
            if not re.match(r'^Ins\s+Total', line, re.IGNORECASE) and not re.match(r'^Address', line, re.IGNORECASE):
                current_block["wrapped_lines"].append(line)
                
        i += 1
        
    if current_block:
        course_blocks.append(current_block)
        
    courses = []
    for block in course_blocks:
        start_line = block["start_line"]
        wrapped = block["wrapped_lines"]
        
        m = re.match(r'^(\d+)\s+([A-Z][A-Z0-9\s&Parentheses()\-\'/,\.]+?)\s+(\d{2,4})\s+(\d{2,4})', start_line)
        if not m:
            # Fallback regex in case of weird characters in name
            m = re.match(r'^(\d+)\s+(.+?)\s+(\d{2,4})\s+(\d{2,4})', start_line)
            
        if m:
            serial = m.group(1)
            course_name_part = m.group(2).strip()
            
            full_course_name = course_name_part
            for wl in wrapped:
                full_course_name += " " + wl.strip()
            
            full_course_name = re.sub(r'\s+', ' ', full_course_name).strip()
            
            rest = start_line[m.start(3):]
            nums = re.findall(r'\d+', rest)
            
            total_intake = int(nums[0])
            total_kea = int(nums[1])
            
            course = {
                "course_name": full_course_name,
                "total_intake": total_intake,
                "total_kea_seats": total_kea,
                "snq_5pct":   int(nums[2]) if len(nums) > 2 else 0,
                "kea_ph":     int(nums[3]) if len(nums) > 3 else 0,
                "kea_spl":    int(nums[4]) if len(nums) > 4 else 0,
                "kea_hk":     int(nums[5]) if len(nums) > 5 else 0,
                "kea_rk":     int(nums[6]) if len(nums) > 6 else 0,
                "kea_tot":    int(nums[7]) if len(nums) > 7 else 0,
                "cat2_seats": 0,
                "cat3_seats": 0,
                "over_above": int(nums[8]) if len(nums) > 8 else 0,
            }

            if annexure in ["C", "D"] and len(nums) >= 10:
                course["cat2_seats"] = int(nums[8])
                course["cat3_seats"] = int(nums[9])
                course["over_above"] = int(nums[10]) if len(nums) > 10 else 0

            courses.append(course)
            
    return courses

# Test on page 86 (SVCE) and page 87 (T.John)
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    # SVCE on page 86
    page = pdf.pages[85]
    text = page.extract_text()
    lines = text.split("\n")
    # find lines for college 134
    svce_lines = []
    found = False
    for line in lines:
        if "134 Sri Venkateshwara College" in line:
            found = True
        elif "135 Srinivas" in line:
            found = False
        if found:
            svce_lines.append(line)
            
    print("SVCE parsed courses:")
    courses = parse_college_courses(svce_lines, "C")
    for c in courses:
        print(f"  - {c['course_name']} (Intake: {c['total_intake']})")

    # T.John on page 87
    page = pdf.pages[86]
    text = page.extract_text()
    lines = text.split("\n")
    # find lines for college 136
    tjohn_lines = []
    found = False
    for line in lines:
        if "136 T.John" in line:
            found = True
        elif "137 The National" in line:
            found = False
        if found:
            tjohn_lines.append(line)
            
    print("\nT.John parsed courses:")
    courses = parse_college_courses(tjohn_lines, "C")
    for c in courses:
        print(f"  - {c['course_name']} (Intake: {c['total_intake']})")
