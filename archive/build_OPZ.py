"""
Build Annexure O (27 colleges), P (2 colleges), Z (2 colleges) from PDF data.
Verify each against grand total from image pages.

Grand Totals from PDF:
  O: 33120 | 13294 | 665 | 142 | 1625 | 10862 | 12487
  P:  2280 |   764 |  38 |   9 |   58 |   659 |   717
  Z:   395 |   395 |  20 |   4 |  30  |  341  |  371  | 20 (over)

Annexure O layout: Private Universities, 40% KEA (no CAT-2/CAT-3 in most)
Annexure P layout: Deemed Universities, variable KEA %
Annexure Z layout: Govt colleges with higher fees, 100% KEA

NOTE: Annexure O total row shows 7 columns: intake|kea|ph|spl|hk|rk|tot
      No CAT-2/CAT-3 split visible - these are university-only quota seats.
"""
import json, sys, pdfplumber, re
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Remove any existing O, P, Z
before = len(d["colleges"])
d["colleges"] = [c for c in d["colleges"] if c["annexure"] not in ("O","P","Z")]
print(f"Removed {before - len(d['colleges'])} old O/P/Z records")

def cr(name, intake, kea, ph, spl, hk, rk, tot, cat2=0, cat3=0, over=0):
    return {"course_name":name, "total_intake":intake, "total_kea_seats":kea,
            "snq_5pct":over, "kea_ph":ph, "kea_spl":spl, "kea_hk":hk, "kea_rk":rk,
            "kea_tot":tot, "cat2_seats":cat2, "cat3_seats":cat3, "over_above_5pct":over}

def col(ann, num, name, addr, dist, cat1, courses):
    return {"college_number":num, "college_name":name, "address":addr,
            "annexure":ann, "college_type": {
                "O":"Private University", "P":"Deemed University",
                "Z":"Government (Higher Fees)"}[ann],
            "district":dist, "cat1_pct":cat1, "cat2_pct":0, "cat3_pct":0,
            "total_intake":sum(c["total_intake"] for c in courses),
            "total_kea_seats":sum(c["total_kea_seats"] for c in courses),
            "courses":courses}

# ════════════════════════════════════════════════════════════════════════════
# ANNEXURE O — Private Universities (40% KEA for most, 50% for Univ of Mysuru)
# Pages 104-118
# ════════════════════════════════════════════════════════════════════════════

# Extract pages 104-117 text automatically
ann_o_text_data = {}
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg in range(104, 118):
        text = pdf.pages[pg-1].extract_text() or ""
        ann_o_text_data[pg] = text

# Parse all O colleges from text using structured extraction
def parse_o_colleges(pages_text):
    """Parse Annexure O colleges from text. Returns list of (num, name, addr, courses)"""
    full_text = "\n".join(pages_text.values())
    colleges = []
    # Split by college number at start of line
    parts = re.split(r'\n(?=\d{1,2}\s+[A-Z][A-Z\s]{5,})', full_text)
    for part in parts:
        lines = part.strip().splitlines()
        if not lines: continue
        m = re.match(r'^(\d{1,2})\s+(.+)', lines[0])
        if not m: continue
        num = int(m.group(1))
        if num < 1 or num > 27: continue
        name = m.group(2).strip()
        addr = ""
        for l in lines[1:]:
            if l.startswith("Address"): addr = l.replace("Address :","").strip(); break
        colleges.append((num, name, addr))
    return colleges

# Build O manually from extracted text (more reliable than regex for course rows)
ann_o = []

# Read each page and parse directly
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg_num in range(104, 118):
        text = pdf.pages[pg_num-1].extract_text() or ""
        # Find college blocks on this page
        # Each college block starts with "N College Name\nAddress: ..."
        for m in re.finditer(
            r'^(\d{1,2})\s+([A-Z][A-Z\s\(\)&\.\,\'\-]+)\nAddress\s*:\s*(.+?)(?=\n\d{1,2}\s+[A-Z]|\nSl\.N|\nANNEX|$)',
            text, re.MULTILINE | re.DOTALL
        ):
            num = int(m.group(1))
            if num > 27: continue
            name = m.group(2).strip()
            addr = m.group(3).strip().split('\n')[0].strip()
            print(f"  Found O-{num}: {name[:50]}")

print()

# ── Build Annexure O manually from PDF text ──────────────────────────────────
# (Using the printed text we already read from pages 104-117 and image pg 118)

ann_o_colleges = [
  # PAGE 104 ─────────────────────────────────────────────────────
  col("O",1,"Adhichunchanagiri University (Formerly B G S Institute of Technology, BG Nagara)",
      "MANDYA","Mandya",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          180, 72,4,1, 5,62,67),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",     60, 24,1,0, 2,21,23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,1, 2,20,22),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21,23),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21,23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    60, 24,1,1, 2,20,22),
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,1, 2,20,22),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21,23),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",         60, 24,1,0, 2,21,23),
    cr("B TECH IN AGRICULTURE ENGINEERING",                    60, 24,1,0, 2,21,23),
    cr("B TECH IN FOOD TECHNOLOGY",                            30, 12,1,0, 1,10,11),
    cr("B TECH IN MEDICAL ELECTRONICS",                        30, 12,1,0, 1,10,11),
  ]),
  col("O",2,"ALLIANCE University",
      "CHIKKAHULLURU VILLAGE, ANEKAL TALUK, BENGALURU","Bangalore",40,[
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",   60, 24,1,1, 2,20,22),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,1, 2,20,22),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          360,144,7,1,11,125,136),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  120, 48,2,1, 4,41,45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     120, 48,2,1, 4,41,45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBSEC)",  60, 24,1,0, 2,21,23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   240, 96,5,1, 7,83,90),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21,23),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",         60, 24,1,1, 2,20,22),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,1, 2,20,22),
    cr("B TECH IN MECHATRONICS",                               60, 24,1,0, 2,21,23),
    cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",       60, 24,1,0, 2,21,23),
    cr("B TECH IN COMPUTER SCIENCE AND TECHNOLOGY (BIG DATA)",120, 48,2,1, 4,41,45),
    cr("B TECH IN COMPUTER SCIENCE AND DESIGN",               120, 48,2,1, 4,41,45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",     60, 24,1,1, 2,20,22),
  ]),
  # PAGE 105 ─────────────────────────────────────────────────────
  col("O",3,"AMITY UNIVERSITY",
      "MYSORE ROAD, BENGALURU","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          360,144,7,1,11,125,136),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  180, 72,4,1, 5,62,67),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   180, 72,4,1, 5,62,67),
  ]),
  col("O",4,"CMR University",
      "BANGALORE","Bangalore",40,[
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",   60, 24,1,0, 2,21,23),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21,23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          360,144,7,1,11,125,136),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  120, 48,2,1, 4,41,45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     120, 48,2,1, 4,41,45),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,1, 2,20,22),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   180, 72,4,1, 5,62,67),
  ]),
  # PAGE 106 ─────────────────────────────────────────────────────
  col("O",5,"Dayananda Sagar University",
      "SHAVIGE MALLESHWARA HILLS, KUMARASWAMY LAYOUT, BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          600,240,12,1,18,209,227),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  240, 96,5,1, 7,83, 90),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     240, 96,5,1, 7,83, 90),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",    120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBSEC)", 120, 48,2,1, 4,41, 45),
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",  120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   240, 96,5,1, 7,83, 90),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21, 23),
    cr("B TECH IN CIVIL ENGINEERING",                         120, 48,2,1, 4,41, 45),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",         60, 24,1,1, 2,20, 22),
    cr("B TECH IN ROBOTICS AND AUTOMATION",                    60, 24,1,1, 2,20, 22),
    cr("B TECH IN BIOTECHNOLOGY",                             120, 48,2,1, 4,41, 45),
    cr("B TECH IN AEROSPACE ENGINEERING",                     180, 72,4,1, 5,62, 67),
    cr("B TECH IN CHEMICAL ENGINEERING",                       60, 24,1,0, 2,21, 23),
  ]),
  # PAGE 107 ─────────────────────────────────────────────────────
  col("O",6,"Garden City University",
      "BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          300,120,6,1, 9,104,113),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  180, 72,4,1, 5,62, 67),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   180, 72,4,1, 5,62, 67),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
  ]),
  col("O",7,"GM University",
      "DAVANAGERE","Davanagere",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          240, 96,5,1, 7,83, 90),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0, 2,21, 23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",     60, 24,1,1, 2,20, 22),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBSEC)",  60, 24,1,0, 2,21, 23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41, 45),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21, 23),
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",  180, 72,4,1, 5,62, 67),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",        120, 48,2,1, 4,41, 45),
    cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",       60, 24,1,0, 2,21, 23),
  ]),
  # PAGE 108 ─────────────────────────────────────────────────────
  col("O",8,"JSS Science and Technology University",
      "JSS TECHNICAL INSTITUTIONS CAMPUS, MYSORE","Mysuru",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          240, 96,5,1, 7,83, 90),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",   60, 24,1,0, 2,21, 23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0, 2,21, 23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21, 23),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21, 23),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",         60, 24,1,1, 2,20, 22),
    cr("B TECH IN MECHATRONICS",                               60, 24,1,0, 2,21, 23),
    cr("B TECH IN BIOTECHNOLOGY",                              60, 24,1,1, 2,20, 22),
  ]),
  col("O",9,"K L E Technological University, Belgaum Campus",
      "VIDYANAGAR, HUBLI","Dharwad",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          180, 72,4,1, 5,62, 67),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",   60, 24,1,0, 2,21, 23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0, 2,21, 23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    60, 24,1,0, 2,21, 23),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,1, 2,20, 22),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21, 23),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",         60, 24,1,0, 2,21, 23),
  ]),
  # PAGE 109 ─────────────────────────────────────────────────────
  col("O",10,"Khaja Bandanawaz University",
      "KALABURAGI","Kalaburagi",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",   60, 24,1,0, 2,21, 23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    60, 24,1,1, 2,20, 22),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21, 23),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
  ]),
  col("O",11,"KISHKINDA UNIVERSITY",
      "RAICHUR ROAD, GANGAVATHI, KOPPAL DIST","Koppal",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          480,192,10,1,14,167,181),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41, 45),
    cr("B TECH IN MECHANICAL ENGINEERING",                    120, 48,2,1, 4,41, 45),
  ]),
  # PAGE 110 ─────────────────────────────────────────────────────
  col("O",12,"KLE Technological University (Formerly BVBCET)",
      "VIDYANAGAR, HUBLI","Dharwad",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          360,144,7,1,11,125,136),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  180, 72,4,1, 5,62, 67),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   300,120,6,1, 9,104,113),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41, 45),
    cr("B TECH IN MECHANICAL ENGINEERING",                    240, 96,5,1, 7,83, 90),
    cr("B TECH IN CIVIL ENGINEERING",                         120, 48,2,1, 4,41, 45),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",        120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBSEC)",  60, 24,1,1, 2,20, 22),
  ]),
  # PAGE 111 ─────────────────────────────────────────────────────
  col("O",13,"M . S . Ramaiah University of Applied Sciences",
      "GNANAGANGOTHRI CAMPUS, BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          180, 72,4,1, 5,62, 67),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",      60, 24,1,0, 2,21, 23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBSEC)",  60, 24,1,0, 2,21, 23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0, 2,21, 23),
    cr("B TECH IN MECHANICAL ENGINEERING",                     60, 24,1,0, 2,21, 23),
    cr("B TECH IN CIVIL ENGINEERING",                          60, 24,1,0, 2,21, 23),
    cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",       60, 24,1,0, 2,21, 23),
    cr("B TECH IN BIOTECHNOLOGY",                              60, 24,1,1, 2,20, 22),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",        120, 48,2,1, 4,41, 45),
  ]),
  col("O",14,"PES University",
      "100 FEET RING ROAD, BSK III STAGE, BANGALORE","Bangalore",50,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          720,360,18,1,22,319,341),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   360,180,9,1,11,159,170),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      180, 90,5,1, 5, 79, 84),
    cr("B TECH IN MECHANICAL ENGINEERING",                    240,120,6,1, 7,106,113),
    cr("B TECH IN BIOTECHNOLOGY",                              60, 30,2,0, 2, 26, 28),
    cr("B TECH IN CIVIL ENGINEERING",                         240,120,6,1, 7,106,113),
  ]),
  # PAGE 112 ─────────────────────────────────────────────────────
  col("O",15,"PES UNIVERSITY (Electronic City Campus)",
      "ELECTRONIC CITY, BANGALORE","Bangalore",50,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          720,360,18,1,22,319,341),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   360,180,9,1,11,159,170),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      180, 90,5,1, 5, 79, 84),
  ]),
  col("O",16,"PRESIDENCY University",
      "ITGALPURA, RAJANUKUNTE, YELAHANKA, BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          720,288,14,1,22,251,273),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  480,192,10,1,14,167,181),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DS)",     360,144,7,1,11,125,136),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBSEC)", 240, 96,5,1, 7,83, 90),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",    120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   360,144,7,1,11,125,136),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41, 45),
    cr("B TECH IN CIVIL ENGINEERING",                         120, 48,2,1, 4,41, 45),
    cr("B TECH IN MECHANICAL ENGINEERING",                    120, 48,2,1, 4,41, 45),
    cr("B TECH IN INFORMATION SCIENCE AND TECHNOLOGY",        180, 72,4,1, 5,62, 67),
    cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",      120, 48,2,1, 4,41, 45),
    cr("B TECH IN MECHATRONICS",                               60, 24,1,0, 2,21, 23),
    cr("B TECH IN BIOTECHNOLOGY",                              60, 24,1,1, 2,20, 22),
    cr("B TECH IN AEROSPACE ENGINEERING",                      60, 24,1,1, 2,20, 22),
    cr("B TECH IN COMPUTER SCIENCE AND DESIGN",               120, 48,2,1, 4,41, 45),
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",  180, 72,4,1, 5,62, 67),
  ]),
  # PAGE 113 ─────────────────────────────────────────────────────
  col("O",17,"RAI TECHNOLOGICAL UNIVERSITY",
      "11TH MILE GALLU, DODDABALLAPUR-NELAMANGALA ROAD, BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          120, 48,3,1, 3,41, 44),
    cr("B TECH IN INFORMATION TECHNOLOGY",                     60, 24,1,1, 2,20, 22),
  ]),
  col("O",18,"REVA University",
      "RUKMINI KNOWLEDGE PARK, KATTIGENAHALLI, YELAHANKA, BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND INFORMATION TECHNOLOGY",180,72,4,1, 5,62, 67),
    cr("B TECH IN AERO SPACE ENGINEERING",                     60, 24,1,1, 2,20, 22),
    cr("B TECH IN AGRICULTURAL ENGINEERING",                   30, 12,1,0, 1,10, 11),
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",  180, 72,4,1, 5,62, 67),
    cr("B TECH IN CIVIL ENGINEERING",                         120, 48,2,1, 4,41, 45),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI/ML)",  270,108,6,1, 8,93,101),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          360,144,7,1,11,125,136),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",     60, 24,1,1, 2,20, 22),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",      120, 48,2,1, 4,41, 45),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   240, 96,5,1, 7,83, 90),
    cr("B TECH IN ELECTRONICS & COMPUTER ENGINEERING",         60, 24,1,0, 2,21, 23),
    cr("B TECH IN INFORMATION SCIENCE ENGINEERING",           120, 48,2,1, 3,42, 45),
    cr("B TECH IN MECHANICAL ENGINEERING",                    120, 48,3,1, 3,41, 44),
    cr("B TECH IN MECHATRONICS ENGINEERING",                   60, 24,1,1, 2,20, 22),
    cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",       60, 24,1,1, 2,20, 22),
  ]),
  # PAGE 115 ─────────────────────────────────────────────────────
  col("O",19,"RV University",
      "R.V. VIDYANIKETAN POST, MYSORE ROAD, BANGALORE","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          540,216,11,1,16,188,204),
  ]),
  col("O",20,"SAPTHAGIRI NPS UNIVERSITY",
      "#14/5, CHIKKASANDRA, HESARAGHATTA MAIN ROAD, BANGALURU","Bangalore",40,[
    cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)", 780,312,16,1,24,271,295),
    cr("COMPUTER SCIENCE AND ENGINEERING",                   2580,1032,51,1,78,902,980),
    cr("COMPUTER SCIENCE AND ENGINEERING (AI & DATA SCIENCE)", 240,96, 5,1, 7,83, 90),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",     420,168, 8,1,13,146,159),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",                 60, 24, 1,0, 2,21, 23),
    cr("ELECTRONICS AND COMMUNICATION ENGG",                  240, 96, 5,1, 7,83, 90),
  ]),
  col("O",21,"School of Planning and Architecture, University of Mysore",
      "2ND FLOOR, SENATE BHAVAN, MANASAGANGOTRI P.O., MYSORE","Mysuru",50,[
    cr("B.PLAN",40,20,1,0,1,18,19),
  ]),
  # PAGE 116 ─────────────────────────────────────────────────────
  col("O",22,"Sharanbasava University (Exclusively for Women) (Formerly Goduati Engineering College For Women)",
      "SHARNBASVESHWARA INSTITUTIONS CAMPUS, KALABURAGI-585103, KARNATAKA","Kalaburagi",40,[
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,1,15, 7,22),
    cr("B TECH IN CIVIL ENGINEERING",                           30,12,1,0, 8, 3,11),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           150,60,3,1,39,17,56),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",        60,24,1,1,15, 7,22),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    120,48,2,1,32,13,45),
  ]),
  col("O",23,"Sharanbasava University (Formerly Appa Institute of Engineering and Technology)",
      "SHARNBASVESHWARA INSTITUTIONS CAMPUS, KALABURAGI-585103, KARNATAKA","Kalaburagi",40,[
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",   60, 24,1,1,15, 7,22),
    cr("B TECH IN CIVIL ENGINEERING",                         120, 48,3,1,31,13,44),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          180, 72,4,1,47,20,67),
    cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       60, 24,1,0,16, 7,23),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",   120, 48,3,1,31,13,44),
    cr("B TECH IN ENERGY ENGINEERING",                         60, 24,1,0,16, 7,23),
    cr("B TECH IN MECHANICAL ENGINEERING",                    120, 48,2,1,32,13,45),
    cr("BTECH IN COMPUTER SCIENCE AND DESIGN",                 60, 24,1,0,16, 7,23),
  ]),
  # PAGE 117 ─────────────────────────────────────────────────────
  col("O",24,"Srinivas University",
      "SRINIVAS CAMPUS MUKKA MANGALURU","Dakshina Kannada",40,[
    cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",120,48,2,1, 3,42,45),
    cr("B TECH IN CIVIL ENGINEERING",                           60,24,1,0, 2,21,23),
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           180,72,4,1, 5,62,67),
    cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",     30,12,1,0, 1,10,11),
    cr("B TECH IN MECHANICAL ENGINEERING",                      60,24,1,1, 2,20,22),
    cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",     60,24,1,1, 2,20,22),
  ]),
  col("O",25,"THE CHANAKYA UNIVERSITY",
      "NO 29 HARALURU, DEVANAHALLI TALUK (NEAR BENGALURU INTERNATIONAL AIRPORT)","Bangalore",40,[
    cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          120, 48,2,1, 4,41,45),
    cr("B.Tech In BIOTECHNOLOGY & BIO-ENGINEERING",            60, 24,1,0, 2,21,23),
    cr("B.TECH IN CIVIL CONSTRUCTION AND SUSTAINABILITY ENGG", 60, 24,1,1, 2,20,22),
    cr("B.TECH IN COMPUTER SCIENCE AND ARTIFICIAL INTELLIGENCE",120,48,3,1, 3,41,44),
    cr("B.TECH IN ELECTRICAL ENGINEERING AND COMPUTER SCIENCE", 60, 24,1,1, 2,20,22),
    cr("B.TECH IN ELECTRONICS ENGINEERING (VLSI AND EMBEDDED)", 120,48,3,1, 3,41,44),
    cr("B.TECH IN MECHANICAL AND AEROSPACE ENGINEERING",        60, 24,1,0, 2,21,23),
  ]),
  # PAGE 118 (image) ────────────────────────────────────────────
  col("O",26,"University of Mysuru",
      "B.N.BAHADUR INSTITUTE OF MANAGEMENT SCIENCES, DOS IN BUSINESS ADMINISTRATION, UNIVERSITY OF MYSORE, MANASAGANGOTRI, HUNSUR ROAD, MYSORE","Mysuru",50,[
    cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",  60, 30,2,0, 2,26,28),
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",90,45,2,0, 4,39,43),
    cr("BIOMEDICAL AND ROBOTIC ENGINEERING",         60, 30,2,0, 2,26,28),
    cr("CIVIL ENVIRONMENTAL ENGINEERING",            30, 15,1,0, 1,13,14),
    cr("COMPUTER SCIENCE AND DESIGN",               120, 60,3,1, 5,51,56),
    cr("COMPUTER SCIENCE AND ENGINEERING",           60, 30,1,0, 2,27,29),
  ]),
  col("O",27,"Vidyashilp University",
      "#125, BETTENAHALLI, KUNDANA HOBLI, CHAPPARKALLU RD, BENGALURU, KARNATAKA 562110","Bangalore",40,[
    cr("B TECH (HONS) COMPUTER SCIENCE AND ENGINEERING AND ENGINEERING (DATA SCIENCE)",120,48,2,1,4,41,45),
  ]),
]

d["colleges"].extend(ann_o_colleges)
print(f"Added {len(ann_o_colleges)} Annexure O colleges")

# ════════════════════════════════════════════════════════════════════════════
# ANNEXURE P — Deemed Universities (variable KEA %)
# Pages 119 (text) + 120 (image)
# ════════════════════════════════════════════════════════════════════════════
ann_p_colleges = [
  col("P",1,"GANDHI INSTITUTE OF TECHNOLOGY AND MANAGEMENT (GITAM) OFF CAMPUS BENGALURU",
      "NH 207, NAGADENEHALLI, DODDABALLAPUR TALUK, BENGALURU-561203","Bangalore",28,[
    cr("CIVIL ENGINEERING WITH COMPUTER APPLICATION",  30, 12,1,0, 1,10,11),
    cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",360,90,5,1, 7,77,84),
    cr("COMPUTER SCIENCE AND ENGINEERING",             420,105,5,1, 8,91,99),
    cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",60,15,1,0, 1,13,14),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",  120,30,1,1, 2,26,28),
    cr("ELECTRICAL & COMPUTER ENGINEERING",             30, 12,0,0, 1,11,12),
    cr("ELECTRONICS ENGINEERING (VLSI DESIGN & TECHNOLOGY)",30,12,1,1, 1, 9,10),
    cr("ELECTRONICS AND COMMUNICATION ENGG",           120, 48,2,1, 3,42,45),
    cr("MECHANICAL ENGINEERING",                        30, 12,1,0, 1,10,11),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",          30,  8,0,0, 1, 7, 8),
  ]),
  col("P",2,"Sri Siddhartha Institute of Technology",
      "MARALUR, TUMKUR","Tumkur",40,[
    cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",  60, 24,1,0, 2,21,23),
    cr("BIO-MEDICAL ENGINEERING",                       30, 12,1,0, 1,10,11),
    cr("CIVIL ENGINEERING",                             60, 24,1,0, 2,21,23),
    cr("COMPUTER SCIENCE AND ENGINEERING",             180, 72,4,1, 5,62,67),
    cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",60,24,1,0,2,21,23),
    cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",  60,24,1,0,2,21,23),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",         120, 48,3,1, 3,41,44),
    cr("ELECTRONICS AND COMMUNICATION ENGG",           180, 72,4,1, 5,62,67),
    cr("ELECTRONICS AND TELECOMMUNICATION ENGINEERING", 60, 24,1,0, 2,21,23),
    cr("INFORMATION SCIENCE AND ENGINEERING",          120, 48,2,1, 4,41,45),
    cr("MECHANICAL ENGINEERING",                        60, 24,1,0, 2,21,23),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",          60, 24,1,0, 2,21,23),
  ]),
]
d["colleges"].extend(ann_p_colleges)
print(f"Added {len(ann_p_colleges)} Annexure P colleges")

# ════════════════════════════════════════════════════════════════════════════
# ANNEXURE Z — Government Colleges with Higher Fees (100% KEA)
# Page 121 (image)
# ════════════════════════════════════════════════════════════════════════════
ann_z_colleges = [
  col("Z",1,"Constituent College of VTU, Chintamani Chikaballapura",
      "DIST CHIKBALLAPURA","Chikballapura",100,[
    cr("COMPUTER SCIENCE AND ENGINEERING",                30,30,2,0, 2,26,28, over=1),
    cr("COMPUTER SCIENCE AND ENGINEERING (AI/ML)",        30,30,2,1, 2,25,27, over=1),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",            30,30,1,0, 2,27,29, over=2),
    cr("ELECTRONICS AND COMMUNICATION ENGG",              30,30,1,0, 3,26,29, over=2),
  ]),
  col("Z",2,"University B.D.T College of Engineering, Davanagere",
      "P J EXTENSION, HADADI ROAD, DAVENGERE","Davanagere",100,[
    cr("CIVIL ENGINEERING",                               30,30,1,0, 2,27,29, over=2),
    cr("COMPUTER SCIENCE AND ENGINEERING",                60,60,3,1, 5,51,56, over=3),
    cr("ELECTRICAL & ELECTRONICS ENGINEERING",            30,30,1,0, 2,27,29, over=2),
    cr("ELECTRONICS AND COMMUNICATION ENGG",              60,60,3,1, 5,51,56, over=3),
    cr("ELECTRONICS AND INSTRUMENTATION ENGINEERING",     30,30,2,0, 2,26,28, over=1),
    cr("MECHANICAL ENGINEERING",                          35,35,2,1, 3,29,32, over=2),
    cr("ROBOTICS AND ARTIFICIAL INTELLIGENCE",            30,30,2,0, 2,26,28, over=1),
  ]),
]
d["colleges"].extend(ann_z_colleges)
print(f"Added {len(ann_z_colleges)} Annexure Z colleges")

with open("seat_matrix_data.json","w",encoding="utf-8") as f:
    json.dump(d,f,indent=2,ensure_ascii=False)

# ── Verification ──────────────────────────────────────────────────────────────
def verify(ann, pdf_totals, label_map):
    cols = [c for c in d["colleges"] if c["annexure"]==ann]
    s = {k:0 for k in pdf_totals}
    for c in cols:
        for cr_rec in c["courses"]:
            s["intake"] += cr_rec.get("total_intake",0)
            s["kea"]    += cr_rec.get("total_kea_seats",0)
            s["ph"]     += cr_rec.get("kea_ph",0)
            s["spl"]    += cr_rec.get("kea_spl",0)
            s["hk"]     += cr_rec.get("kea_hk",0)
            s["rk"]     += cr_rec.get("kea_rk",0)
            s["tot"]    += cr_rec.get("kea_tot",0)
            if "over" in s: s["over"] += cr_rec.get("over_above_5pct",0)
    sep = "-"*66
    print(f"\n{sep}")
    print(f"  ANNEXURE {ann} VERIFICATION vs PDF Grand Total")
    print(sep)
    all_ok = True
    for k,pv in pdf_totals.items():
        ov=s[k]; diff=ov-pv
        ok="OK" if diff==0 else f"OFF {diff:+d}"
        if diff!=0: all_ok=False
        print(f"  {label_map[k]:<22} {pv:>8} {ov:>8} {diff:>+8}  {ok}{'  <---' if diff!=0 else ''}")
    print(sep)
    print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'MISMATCHES'}")
    print(f"  Colleges: {len(cols)}")
    return all_ok

LABELS = {"intake":"Total Intake","kea":"Total KEA","ph":"PH 5%","spl":"SPL",
          "hk":"HK","rk":"RK","tot":"TOT HK-RK","over":"Over SNQ 5%"}

verify("O", {"intake":33120,"kea":13294,"ph":665,"spl":142,"hk":1625,"rk":10862,"tot":12487}, LABELS)
verify("P", {"intake":2280, "kea":764,  "ph":38, "spl":9,  "hk":58,  "rk":659,  "tot":717},  LABELS)
verify("Z", {"intake":395,  "kea":395,  "ph":20, "spl":4,  "hk":30,  "rk":341,  "tot":371,  "over":20}, LABELS)
