"""
Write the full robust parser state machine that parses course name, intake, KEA RK, KEA HK, PH RK/HK, SPL RK/HK, etc.
It tracks the current active college name, active course (RK), and attaches HK rows and KM QUOTA rows to it.
"""
import pdfplumber, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")

def parse_pdf(pdf_path, pages):
    colleges = []
    
    current_college = None
    current_college_num = None
    current_courses = []
    
    # State tracking for course-level assembly
    current_course = None # holds active RK course dict
    
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pages:
            text = pdf.pages[pg-1].extract_text() or ""
            lines = text.splitlines()
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Check for college header (starts with number and college name)
                # Avoid matching course rows that might start with a number (none of them start with numbers, they start with RK or HK)
                m_hdr = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$', stripped)
                if m_hdr:
                    # Save previous college
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
                    continue
                
                # TOT row: marks page total
                if stripped.startswith("TOT ") or stripped.startswith("TOT\t"):
                    # Save the current course if any before total
                    if current_course:
                        current_courses.append(current_course)
                        current_course = None
                    continue
                
                # Header rows to ignore
                if stripped.startswith("Intake") or stripped.startswith("Cat Tot") or "government notification" in stripped.lower():
                    continue
                
                # RK row: e.g. "RK CS 30 27 1 0 4 2 0 0 0 0 1 0 1 21 9 4 1 1 3 1 1 1"
                # Sometimes course names can contain digits or other characters: we match RK, course name, then intake, KEA RK, PH, SPL.
                m_rk = re.match(r'^RK\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_rk:
                    # Save previous course if any
                    if current_course:
                        current_courses.append(current_course)
                        
                    course_name = m_rk.group(1).strip()
                    intake = int(m_rk.group(2))
                    kea_rk = int(m_rk.group(3))
                    ph_rk = int(m_rk.group(4))
                    spl_rk = int(m_rk.group(5))
                    
                    current_course = {
                        "name": course_name,
                        "intake": intake,
                        "kea_rk": kea_rk,
                        "kea_hk": 0,
                        "ph_rk": ph_rk,
                        "ph_hk": 0,
                        "spl_rk": spl_rk,
                        "spl_hk": 0
                    }
                    continue
                
                # HK row: e.g. "HK 2 0 0 0 0 0 0 0 0 0 2 1 1 0 0 0 0 0 0"
                m_hk = re.match(r'^HK\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_hk:
                    kea_hk = int(m_hk.group(1))
                    ph_hk = int(m_hk.group(2))
                    spl_hk = int(m_hk.group(3))
                    
                    if current_course:
                        current_course["kea_hk"] = kea_hk
                        current_course["ph_hk"] = ph_hk
                        current_course["spl_hk"] = spl_hk
                    continue
                
                # KM QUOTA row (ignore/skip for KEA seats totals because it's not a primary course row)
                if "KM QUOTA" in stripped:
                    continue
                    
        # Append final college
        if current_college_num is not None:
            colleges.append({
                "num": current_college_num,
                "name": current_college,
                "courses": current_courses
            })
            
    return colleges

# Verify E and V overall calculated sums vs page-level TOT sums
colleges_e = parse_pdf("Seat_Matrix_05072025.pdf", range(122, 324))
colleges_v = parse_pdf("Seat_Matrix_05072025.pdf", range(325, 361))

def print_summary(ann_name, cols):
    total_intake = 0
    total_kea = 0
    total_ph = 0
    total_spl = 0
    total_hk = 0
    total_rk = 0
    
    for c in cols:
        for cr in c["courses"]:
            total_intake += cr["intake"]
            total_kea += cr["kea_rk"] + cr["kea_hk"]
            total_ph += cr["ph_rk"] + cr["ph_hk"]
            total_spl += cr["spl_rk"] + cr["spl_hk"]
            total_hk += cr["kea_hk"]
            total_rk += cr["kea_rk"]
            
    print(f"\nAnnexure {ann_name} Aggregated totals:")
    print(f"  Colleges: {len(cols)}")
    print(f"  Intake:   {total_intake:,}")
    print(f"  KEA:      {total_kea:,}")
    print(f"  PH:       {total_ph:,}")
    print(f"  SPL:      {total_spl:,}")
    print(f"  HK:       {total_hk:,}")
    print(f"  RK:       {total_rk:,}")

print_summary("E", colleges_e)
print_summary("V", colleges_v)
