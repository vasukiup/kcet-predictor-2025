"""
Run a full parse of all courses in Annexures E and V using our candidate course-level parser.
Let's see if there are any parsing errors, and what the overall aggregated counts are for E and V.
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

def parse_full_annexure(pdf_path, pages, ann_name):
    total_intake = 0
    total_kea = 0
    total_ph = 0
    total_spl = 0
    total_hk = 0
    total_rk = 0
    
    colleges = []
    current_college = None
    college_num = None
    college_courses = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pages:
            text = pdf.pages[pg-1].extract_text() or ""
            lines = text.splitlines()
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Check for college header: e.g., "1 CONSTITUENT COLLEGE OF..."
                m_hdr = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$', stripped)
                if m_hdr:
                    if college_courses and college_num is not None:
                        colleges.append({
                            "num": college_num,
                            "name": current_college,
                            "courses": college_courses
                        })
                    college_num = int(m_hdr.group(1))
                    current_college = m_hdr.group(2).strip()
                    college_courses = []
                    continue
                
                if stripped.startswith("TOT") or stripped.startswith("Intake") or stripped.startswith("Cat Tot") or stripped.startswith("KM QUOTA") or "government notification" in stripped.lower():
                    continue
                
                # Parse RK row
                m_rk = re.match(r'^RK\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_rk:
                    course_name = m_rk.group(1).strip()
                    intake = int(m_rk.group(2))
                    kea_rk = int(m_rk.group(3))
                    ph = int(m_rk.group(4))
                    spl = int(m_rk.group(5))
                    
                    college_courses.append({
                        "name": course_name,
                        "intake": intake,
                        "kea_rk": kea_rk,
                        "kea_hk": 0,
                        "ph": ph,
                        "spl": spl
                    })
                    
                    total_intake += intake
                    total_kea += kea_rk
                    total_rk += kea_rk
                    total_ph += ph
                    total_spl += spl
                    continue
                
                # Parse HK row
                m_hk = re.match(r'^HK\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_hk:
                    kea_hk = int(m_hk.group(1))
                    ph_hk = int(m_hk.group(2))
                    spl_hk = int(m_hk.group(3))
                    
                    if college_courses:
                        college_courses[-1]["kea_hk"] = kea_hk
                        # Wait, we already added RK PH/SPL, does HK have extra PH/SPL?
                        # Yes, we add them to total PH/SPL
                        total_ph += ph_hk
                        total_spl += spl_hk
                    
                    total_kea += kea_hk
                    total_hk += kea_hk
                    continue
                    
        # Add last college
        if college_courses and college_num is not None:
            colleges.append({
                "num": college_num,
                "name": current_college,
                "courses": college_courses
            })
            
    print(f"\nAnnexure {ann_name} Parsing Complete:")
    print(f"  Colleges parsed: {len(colleges)}")
    print(f"  Calculated Intake: {total_intake:,}")
    print(f"  Calculated KEA:    {total_kea:,}")
    print(f"  Calculated PH:     {total_ph:,}")
    print(f"  Calculated SPL:    {total_spl:,}")
    print(f"  Calculated HK:     {total_hk:,}")
    print(f"  Calculated RK:     {total_rk:,}")
    return colleges

# Run E and V
colleges_e = parse_full_annexure("Seat_Matrix_05072025.pdf", range(122, 324), "E")
colleges_v = parse_full_annexure("Seat_Matrix_05072025.pdf", range(325, 361), "V")
