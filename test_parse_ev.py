"""
Parse all course lines, HK lines, KM lines, and build clean summaries.
Let's see if we can parse each course block:
A course block starts with a row like:
`RK CS 30 27 1 0 4 2 0 0 0 0 1 0 1 21 9 4 1 1 3 1 1 1`
followed optionally by:
`KM QUOTA 2 1 1 0 0 0 0 0 0`
`HK 2 0 0 0 0 0 0 0 0 0 2 1 1 0 0 0 0 0 0`
`KM QUOTA 0 0 0 0 0 0 0 0 0`

Let's study the numbers:
CS course:
RK row: intake = 30, KEA seats = 27. PH = 1, SPL = 0. Rur = 4, Urb = 21 (wait: 4 rur + 21 urb = 25. 25 + 1 PH + 0 SPL = 26. Where is the remaining 1 seat? Ah, KM QUOTA RK has 2 seats! Wait, 27 total KEA?
Let's check the HK row:
HK row: HK KEA seats = 2. PH = 0, SPL = 0. Rur = 0, Urb = 2. 2 KEA seats.
KM QUOTA HK row: 0 seats.
Let's sum the KEA seats for CS:
RK KEA = 27
HK KEA = 2
Total KEA = 29.
But wait! The intake is 30. Where is the 30th seat?
Ah! Let's check the KM QUOTA rows:
RK KM QUOTA has 2 seats.
Wait, let's sum: RK CS has 27 KEA seats. Underneath it: KM QUOTA has 2 seats.
HK has 2 seats. Underneath it: KM QUOTA has 0 seats.
Total KEA seats = RK KEA (27) + HK KEA (2) = 29.
Wait, is KEA seats total 27 + 2 = 29?
Let's check the college total at the bottom of page 122:
`TOT 240 226 12 2 34 16 6 2 0 4 2 2 2 181 80 32 14 6 28 6 6 9`
`KM QUOTA 11 4 3 0 1 1 0 2 0`
Wait!
Let's sum the RK seats across the 8 courses:
Courses on page 122:
1. CS: RK = 27, HK = 2. Total KEA = 29.
2. CS AIML: RK = 26, HK = 2. Total KEA = 28.
3. EC: RK = 25, HK = 2. Total KEA = 27.
4. EE: RK = 26, HK = 3. Total KEA = 29.
5. CS: RK = 26, HK = 2. Total KEA = 28.
6. CS AIML: RK = 25, HK = 2. Total KEA = 27.
7. EC: RK = 26, HK = 3. Total KEA = 29.
8. EE: RK = 27, HK = 2. Total KEA = 29.
Total KEA seats for the 8 courses = 29 + 28 + 27 + 29 + 28 + 27 + 29 + 29 = 226.
Yes! 226 is exactly the KEA total printed in the TOT row: `TOT 240 226 ...`
And what about intake?
Each of the 8 courses has intake = 30.
8 * 30 = 240.
This matches the intake total of 240 perfectly!
So:
Total Intake = sum of intake in the RK rows (since HK rows do not have an intake column - the first number on the HK row is KEA seats!).
Total KEA seats = sum of KEA seats in RK rows + KEA seats in HK rows!
Let's double check this rule:
For each course:
- RK row: has Course Name, Intake, KEA seats, PH, SPL, etc.
- HK row: has KEA seats, PH, SPL, etc. (no separate intake, since it's part of the same course intake).
So Course Total Intake = RK row intake.
Course Total KEA = RK row KEA seats + HK row KEA seats.
Let's verify this on page 122:
CS course 1: RK intake = 30, RK KEA = 27. HK KEA = 2. Total KEA = 29.
Is this correct? Yes, because 27 + 2 = 29.
Let's write a script to parse this structure for ALL pages in E and V, sum the totals, and print the calculated totals!
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

def parse_annexure(pdf_path, pages):
    total_intake = 0
    total_kea = 0
    total_ph = 0
    total_spl = 0
    total_hk = 0
    total_rk = 0
    
    current_college = None
    
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pages:
            text = pdf.pages[pg-1].extract_text() or ""
            lines = text.splitlines()
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Check for college header
                m_hdr = re.match(r'^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$', stripped)
                if m_hdr:
                    current_college = m_hdr.group(2).strip()
                    continue
                
                # We want to skip TOT lines, header lines, etc.
                if stripped.startswith("TOT") or stripped.startswith("Intake") or stripped.startswith("Cat Tot") or stripped.startswith("KM QUOTA") or "government notification" in stripped.lower():
                    continue
                
                # Parse RK row: starts with "RK <CourseCode> <intake> <kea_seats> <ph> <spl> ..."
                # Wait, course code is usually uppercase characters, e.g., CS, EC, EE, CS AIML, B Tech in CE CA, etc.
                # Let's match: "RK " followed by course code/name, then numbers.
                m_rk = re.match(r'^RK\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_rk:
                    course_name = m_rk.group(1).strip()
                    intake = int(m_rk.group(2))
                    kea_rk = int(m_rk.group(3))
                    ph = int(m_rk.group(4))
                    spl = int(m_rk.group(5))
                    
                    total_intake += intake
                    total_kea += kea_rk
                    total_rk += kea_rk
                    total_ph += ph
                    total_spl += spl
                    continue
                
                # Parse HK row: starts with "HK <kea_seats> <ph> <spl> ..."
                m_hk = re.match(r'^HK\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+)$', stripped)
                if m_hk:
                    kea_hk = int(m_hk.group(1))
                    ph_hk = int(m_hk.group(2))
                    spl_hk = int(m_hk.group(3))
                    
                    total_kea += kea_hk
                    total_hk += kea_hk
                    total_ph += ph_hk
                    total_spl += spl_hk
                    continue
                    
    return {
        "intake": total_intake,
        "kea": total_kea,
        "ph": total_ph,
        "spl": total_spl,
        "hk": total_hk,
        "rk": total_rk
    }

print("=== Testing Parser on Annexure E (pages 122-123) ===")
res_e_test = parse_annexure("Seat_Matrix_05072025.pdf", range(122, 124))
print("Calculated:", res_e_test)

print("\n=== Testing Parser on Annexure V (pages 325-326) ===")
res_v_test = parse_annexure("Seat_Matrix_05072025.pdf", range(325, 327))
print("Calculated:", res_v_test)
