"""
FINAL Annexure O rebuild — all 27 colleges with exact course data from PDF images.
Target grand total: 33120 intake | 13294 KEA | 665 PH | 142 SPL | 1625 HK | 10862 RK | 12487 TOT
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)
d["colleges"] = [c for c in d["colleges"] if c["annexure"] != "O"]

def cr(name, intake, kea, ph, spl, hk, rk, tot):
    return {"course_name":name,"total_intake":intake,"total_kea_seats":kea,
            "snq_5pct":0,"kea_ph":ph,"kea_spl":spl,"kea_hk":hk,"kea_rk":rk,
            "kea_tot":tot,"cat2_seats":0,"cat3_seats":0,"over_above_5pct":0}

def col(num, name, addr, dist, cat1, courses):
    return {"college_number":num,"college_name":name,"address":addr,
            "annexure":"O","college_type":"Private University",
            "district":dist,"cat1_pct":cat1,"cat2_pct":0,"cat3_pct":0,
            "total_intake":sum(c["total_intake"] for c in courses),
            "total_kea_seats":sum(c["total_kea_seats"] for c in courses),
            "courses":courses}

ann_o = [
# ── PAGE 104 ─────────────────────────────────────────────────────────────────
col(1,"Adhichunchanagiri University (Formerly B G S Institute of Technology, BG Nagara)",
    "B.G.NAGARA, NAGAMANGALA TALUK, MANDYA DISTRICT-571448","Mandya",40,[
  cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",          60, 24,1,0, 2,21,23),
  cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",        30, 12,1,0, 1,10,11),
  cr("CIVIL ENGINEERING",                                     60, 24,1,0, 2,21,23),
  cr("COMPUTER SCIENCE AND ENGINEERING",                     360,144,7,1,11,125,136),
  cr("ELECTRONICS AND COMMUNICATION ENGG",                   180, 72,4,1, 5,62,67),
  cr("INFORMATION SCIENCE AND ENGINEERING",                   60, 24,1,0, 2,21,23),
  cr("MECHANICAL ENGINEERING",                                30, 12,1,0, 1,10,11),
]),
# ── PAGE 105 ─────────────────────────────────────────────────────────────────
col(2,"ALLIANCE University",
    "CHIKKAHULLURU VILLAGE, ANEKAL TALUK, BENGALURU","Bangalore",40,[
  cr("B TECH IN AERO SPACE ENGINEERING",                     120, 48,3,1, 3,41,44),
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60, 24,1,0, 2,21,23),
  cr("B TECH IN BIO-TECHNOLOGY",                              60, 24,1,1, 2,20,22),
  cr("B TECH IN CIVIL ENGINEERING",                           60, 24,1,0, 2,21,23),
  cr("B TECH IN COMPUTER SCIENCE & ENGG (AI AND FUTURE TECHNOLOGIES)",120,48,2,1,4,41,45),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           800,320,16,1,24,279,303),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",60,24,1,0,2,21,23),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",      60, 24,1,0, 2,21,23),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",        60, 24,1,0, 2,21,23),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    120, 48,3,1, 3,41,44),
  cr("B TECH IN INFORMATION TECHNOLOGY",                      60, 24,1,0, 2,21,23),
  cr("B TECH IN MECHANICAL ENGINEERING",                      60, 24,1,0, 2,21,23),
  cr("B TECH IN COMPUTER ENGINEERING (SOFTWARE PRODUCT DEVELOPMENT)",120,48,3,1,3,41,44),
  cr("BTECH IN IT AUGMENTED REALITY AND VIRTUAL REALITY (AR/VR)",60,24,1,0,2,21,23),
  cr("BTECH IN INFORMATION TECHNOLOGY DATA ANALYTICS",        60, 24,1,0, 2,21,23),
  cr("PRODUCTION ENGINEERING",                                30, 12,1,0, 1,10,11),
]),
# ── PAGE 106 ─────────────────────────────────────────────────────────────────
col(3,"AMITY UNIVERSITY",
    "MYSORE ROAD, BENGALURU","Bangalore",40,[
  cr("B TECH IN BIO-TECHNOLOGY",                              60, 24,1,0, 2,21,23),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           600,240,12,1,18,209,227),
  cr("B TECH IN COMPUTER SCIENCE (AI AND ML)",               300,120,6,1, 9,104,113),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",     60, 24,1,0, 2,21,23),
  cr("B.TECH IN COMPUTER SCIENCE (INTERNET OF THINGS)",       60, 24,2,1, 1,20,21),
  cr("B TECH IN COMPUTER SCIENCE AND ENGG (ROBOTICS)",        60, 24,1,1, 2,20,22),
  cr("B TECH IN COMPUTER SCIENCE AND ENGG (DATA ANALYTICS)",  60, 24,1,1, 2,20,22),
  cr("B.TECH IN ELECTRICAL ENGINEERING (ELECTRIC VEHICLE TECHNOLOGY)",60,24,1,0,2,21,23),
  cr("B TECH IN EMBEDDED SYSTEM AND VLSI",                    60, 24,1,1, 2,20,22),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CLOUD COMPUTING)", 60, 24,1,0, 2,21,23),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING(DEV OPS)",   60, 24,1,0, 2,21,23),
  cr("B.Tech in Computer Science and Engineering(Full Stack Development)", 60, 24,2,0, 1,21,22),
]),
col(4,"CMR University",
    "BANGALORE","Bangalore",40,[
  cr("B TECH IN COMPUTER ENGINEERING",                       120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   180, 72,4,1, 5,62,67),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           360,144,7,1,11,125,136),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",120,48,3,1,3,41,44),
  cr("B TECH IN COMPUTER SCIENCE AND TECHNOLOGY",             60, 24,1,0, 2,21,23),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",     60, 24,1,0, 2,21,23),
  cr("B TECH IN INFORMATION TECHNOLOGY",                      60, 24,1,1, 2,20,22),
]),
# ── PAGE 107 ─────────────────────────────────────────────────────────────────
col(5,"Dayananda Sagar University",
    "SHAVIGE MALLESHWARA HILLS, KUMARASWAMY LAYOUT, BANGALORE","Bangalore",40,[
  cr("B TECH IN AERO SPACE ENGINEERING",                     120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   480,192,10,1,15,166,181),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           900,360,18,1,27,314,341),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (AI AND DS)",180,72, 4,1, 5,62,67),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",180,72,4,1,5,62,67),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",180,72,4,1,5,62,67),
  cr("B TECH IN COMPUTER SCIENCE AND TECHNOLOGY",            180, 72,4,1, 5,62,67),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    180, 72,3,1, 5,63,68),
  cr("B TECH IN MECHANICAL ENGINEERING",                      60, 24,1,0, 2,21,23),
  cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",       120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE AND MEDICAL ENGINEERING",    60, 24,1,1, 2,20,22),
]),
col(6,"Garden City University",
    "BANGALORE","Bangalore",40,[
  cr("B TECH IN COMPUTER SCIENCE",                           180, 72,3,1, 6,62,68),
  cr("B TECH IN INFORMATION TECHNOLOGY",                     180, 72,4,1, 5,62,67),
  cr("B TECH IN ROBOTIC ENGINEERING",                        180, 72,4,1, 5,62,67),
  cr("B TECH IN ELECTRONICS ENGINEERING",                    180, 72,4,1, 5,62,67),
  cr("COMPUTER SCIENCE",                                     180, 72,3,1, 6,62,68),
  cr("INFORMATION SCIENCE",                                  180, 72,4,1, 5,62,67),
]),
# ── PAGE 108 ─────────────────────────────────────────────────────────────────
col(7,"GM University",
    "DAVANAGERE","Davanagere",40,[
  cr("B TECH IN COMPUTER SCIENCE (DATA SCIENCE)",            120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE (CLOUD COMPUTING)",         120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE (CYBER SECURITY)",          120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE (INFORMATION SECURITY)",    120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           240, 96,5,1, 7,83,90),
  cr("B TECH IN COMPUTER SCIENCE (AI AND ML)",               180, 72,4,1, 5,62,67),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       180, 72,4,1, 5,62,67),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    180, 72,4,1, 5,62,67),
  cr("B TECH IN INFORMATION SCIENCE ENGINEERING",            180, 72,4,1, 5,62,67),
  cr("B.TECH IN COMPUTER SCIENCE & ENGG (BUSINESS SYSTEMS)",120, 48,3,1, 3,41,44),
  cr("B.TECH IN COMPUTER SCIENCE (INTERNET OF THINGS)",      120, 48,3,1, 3,41,44),
  cr("BIO-TECHNOLOGY",                                        60, 24,1,1, 2,20,22),
  cr("CIVIL ENGINEERING",                                     60, 24,1,0, 2,21,23),
  cr("ENGINEERING DESIGN",                                    60, 24,1,0, 2,21,23),
  cr("MECHANICAL ENGINEERING",                                60, 24,1,1, 2,20,22),
  cr("ROBOTICS AND AUTOMATION",                               60, 24,1,1, 2,20,22),
]),
# ── PAGE 109 ─────────────────────────────────────────────────────────────────
col(8,"JSS Science and Technology University",
    "JSS TECHNICAL INSTITUTIONS CAMPUS, MYSORE","Mysuru",40,[
  cr("BIO-TECHNOLOGY",                                        60, 24,1,0, 2,21,23),
  cr("CIVIL ENGINEERING",                                     60, 24,1,0, 2,21,23),
  cr("COMPUTER SCIENCE AND BUSINESS SYSTEMS",                120, 48,2,1, 3,42,45),
  cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",   60, 24,1,1, 2,20,22),
  cr("COMPUTER SCIENCE AND ENGINEERING",                     300,120,6,1, 9,104,113),
  cr("COMPUTER SCIENCE AND TECHNOLOGY (EXCLUSIVELY FOR DIFFERENTLY ABLED)",30,12,1,0,1,10,11),
  cr("CONSTRUCTION TECHNOLOGY AND MANAGEMENT",                30, 12,1,0, 1,10,11),
  cr("ELECTRONICS AND COMMUNICATION ENGG",                    60, 24,1,1, 2,20,22),
  cr("INFORMATION SCIENCE AND ENGINEERING",                  180, 72,4,1, 5,62,67),
  cr("MECHANICAL ENGINEERING",                                60, 24,1,1, 2,20,22),
]),
col(9,"K L E Technological University, Belgaum Campus (Formerly KLE Dr M.S. Sheshgiri College of Engineering)",
    "VIDYANAGAR, HUBLI","Dharwad",40,[
  cr("BIO-MEDICAL ENGINEERING",                               30, 12,1,0, 1,10,11),
  cr("CHEMICAL ENGINEERING",                                  60, 24,1,1, 2,20,22),
  cr("CIVIL ENGINEERING",                                     60, 24,1,1, 2,20,22),
  cr("COMPUTER SCIENCE AND ENGG (ARTIFICIAL INTELLIGENCE)",   60, 24,1,0, 2,21,23),
  cr("COMPUTER SCIENCE AND ENGINEERING",                     180, 72,4,1, 5,62,67),
  cr("ELECTRICAL & ELECTRONICS ENGINEERING",                  60, 24,1,0, 2,21,23),
  cr("ELECTRONICS AND COMMUNICATION ENGG",                   120, 48,3,1, 3,41,44),
  cr("MECHANICAL ENGINEERING",                                60, 24,1,0, 2,21,23),
]),
# ── PAGE 110 ─────────────────────────────────────────────────────────────────
col(10,"Khaja Bandanawaz University",
    "KALABURAGI","Kalaburagi",40,[
  cr("AERONAUTICAL ENGINEERING",                              30, 12,1,0, 8, 3,11),
  cr("CIVIL ENGINEERING",                                    120, 48,2,1,31,14,45),
  cr("COMPUTER SCIENCE AND ENGINEERING",                     120, 48,2,1,32,13,45),
  cr("ELECTRONICS AND COMMUNICATION ENGG",                    30, 12,1,0, 8, 3,11),
  cr("MECHANICAL ENGINEERING",                               120, 48,2,1,31,14,45),
]),
col(11,"KISHKINDA UNIVERSITY",
    "RAICHUR ROAD, GANGAVATHI, KOPPAL DIST","Koppal",40,[
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   120, 48,2,1,31,14,45),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           480,192,10,1,127,54,181),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       180, 72,4,1,47,20,67),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    240, 96,5,1,63,27,90),
  cr("BTECH IN PHARMACEUTICAL ENGINEERING",                   60, 24,1,0,16, 7,23),
]),
# ── PAGE 111 ─────────────────────────────────────────────────────────────────
col(12,"KLE Technological University (Formerly BVBCET), Hubli",
    "VIDYANAGAR, HUBLI","Dharwad",40,[
  cr("AUTOMATION AND ROBOTIC ENGINEERING",                    60, 24,1,0, 2,21,23),
  cr("BIO-TECHNOLOGY",                                        60, 24,1,0, 2,21,23),
  cr("CIVIL ENGINEERING",                                    120, 48,2,1, 4,41,45),
  cr("COMPUTER SCIENCE AND ENGG (ARTIFICIAL INTELLIGENCE)",  120, 48,2,1, 4,41,45),
  cr("COMPUTER SCIENCE AND ENGINEERING",                     480,192,10,1,14,167,181),
  cr("ELECTRICAL & ELECTRONICS ENGINEERING",                 180, 72,4,1, 5,62,67),
  cr("ELECTRONICS ENGINEERING (VLSI DESIGN & TECHNOLOGY)",    60, 24,1,0, 2,21,23),
  cr("ELECTRONICS AND COMMUNICATION ENGG",                   540,216,11,1,16,188,204),
  cr("MECHANICAL ENGINEERING",                               180, 72,4,1, 5,62,67),
]),
col(13,"M.S. Ramaiah University of Applied Sciences",
    "GNANAGANGOTHRI CAMPUS, BANGALORE","Bangalore",40,[
  cr("AUTOMOTIVE ENGINEERING",                                30, 12,1,0, 1,10,11),
  cr("B TECH IN AERO SPACE ENGINEERING",                      60, 24,1,1, 1,21,22),
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",180,72,4,1, 5,62,67),
  cr("B TECH IN CIVIL ENGINEERING",                           30, 12,1,0, 1,10,11),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           360,144,7,1,11,125,136),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",        60, 24,1,0, 2,21,23),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",     60, 24,1,1, 2,20,22),
  cr("B TECH IN INFORMATION SCIENCE ENGINEERING",            180, 72,4,1, 5,62,67),
  cr("B TECH IN MATHEMATICS AND COMPUTING",                   30, 12,0,0, 1,11,12),
  cr("B TECH IN MECHANICAL ENGINEERING",                      60, 24,1,1, 2,20,22),
  cr("B TECH IN ROBOTICS ENGINEERING",                        60, 24,1,1, 2,20,22),
]),
# ── PAGE 112 ─────────────────────────────────────────────────────────────────
col(14,"PES University",
    "100 FEET RING ROAD, BSK III STAGE, BANGALORE","Bangalore",40,[
  cr("B TECH IN BIO-TECHNOLOGY",                              60, 24,1,1, 1,21,22),
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   540,216,11,1,16,188,204),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           720,288,15,1,22,250,272),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",        60, 24,1,0, 2,21,23),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    360,144, 7,1,11,125,136),
  cr("B TECH IN MECHANICAL ENGINEERING",                      60, 24,1,1, 2,20,22),
]),
col(15,"PES University (Electronic City Campus)",
    "ELECTRONIC CITY, BANGALORE","Bangalore",40,[
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   360,144, 7,1,11,125,136),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           720,288,14,1,22,251,273),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    180, 72, 4,1, 5,62,67),
]),
# ── PAGE 113 ─────────────────────────────────────────────────────────────────
col(16,"PRESIDENCY University",
    "ITGALPURA, RAJANUKUNTE, YELAHANKA, BANGALORE","Bangalore",40,[
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",   120, 48,3,1, 3,41,44),
  cr("B TECH IN CIVIL ENGINEERING",                           60, 24,1,1, 2,20,22),
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   360,144,7,1,11,125,136),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",          1260,504,25,1,38,440,478),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (BLOCK CHAIN)",60,24,1,0,2,21,23),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",240,96,5,1,7,83,90),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",240,96,5,1,7,83,90),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT)",     120, 48,3,1, 3,41,44),
  cr("B TECH IN COMPUTER SCIENCE AND TECHNOLOGY (BIG DATA)",  60, 24,1,1, 2,20,22),
  cr("B TECH IN COMPUTER SCIENCE AND TECHNOLOGY (DEV OPS)",   60, 24,1,1, 2,20,22),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       120, 48,2,1, 4,41,45),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    240, 96,5,1, 7,83,90),
  cr("B TECH IN INFORMATION SCIENCE & TECHNOLOGY",           120, 48,3,1, 3,41,44),
  cr("B TECH IN INFORMATION SCIENCE ENGINEERING",            120, 48,2,1, 4,41,45),
  cr("B TECH IN MECHANICAL ENGINEERING",                      60, 24,1,0, 2,21,23),
  cr("B TECH IN PETROLEUM ENGINEERING",                       60, 24,1,0, 2,21,23),
  cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",        60, 24,1,0, 2,21,23),
  cr("B.TECH IN VLSI",                                        60, 24,1,1, 2,20,22),
]),
# ── PAGE 114 ─────────────────────────────────────────────────────────────────
col(17,"RAI TECHNOLOGICAL UNIVERSITY",
    "11TH MILE GALLU, DODDABALLAPUR-NELAMANGALA ROAD, BANGALORE","Bangalore",40,[
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           120, 48,3,1, 3,41,44),
  cr("B TECH IN INFORMATION TECHNOLOGY",                      60, 24,1,1, 2,20,22),
]),
col(18,"REVA University",
    "RUKMINI KNOWLEDGE PARK, KATTIGENAHALLI, YELAHANKA, BANGALORE","Bangalore",40,[
  cr("B TECH IN COMPUTER SCIENCE AND INFORMATION TECHNOLOGY",180, 72,4,1, 5,62,67),
  cr("B TECH IN AERO SPACE ENGINEERING",                      60, 24,1,1, 2,20,22),
  cr("B TECH IN AGRICULTURAL ENGINEERING",                    30, 12,1,0, 1,10,11),
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",   180, 72,4,1, 5,62,67),
  cr("B TECH IN CIVIL ENGINEERING",                          120, 48,2,1, 4,41,45),
  cr("B TECH IN COMPUTER SCIENCE & ENGINEERING (AI & ML)",   270,108,6,1, 8,93,101),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           360,144,7,1,11,125,136),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING (IOT INCLUDING BLOCK CHAIN)",60,24,1,1,2,20,22),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",       120, 48,2,1, 4,41,45),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    240, 96,5,1, 7,83,90),
  cr("B TECH IN ELECTRONICS & COMPUTER ENGINEERING",          60, 24,1,0, 2,21,23),
  cr("B TECH IN INFORMATION SCIENCE ENGINEERING",            120, 48,2,1, 3,42,45),
  cr("B TECH IN MECHANICAL ENGINEERING",                     120, 48,3,1, 3,41,44),
  cr("B TECH IN MECHATRONICS ENGINEERING",                    60, 24,1,1, 2,20,22),
  cr("B TECH IN ROBOTICS AND ARTIFICIAL INTELLIGENCE",        60, 24,1,1, 2,20,22),
]),
# ── PAGE 115 ─────────────────────────────────────────────────────────────────
col(19,"RV University",
    "R.V. VIDYANIKETAN POST, MYSORE ROAD, BANGALORE","Bangalore",40,[
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           540,216,11,1,16,188,204),
]),
col(20,"SAPTHAGIRI NPS UNIVERSITY",
    "#14/5, CHIKKASANDRA, HESARAGHATTA MAIN ROAD, BANGALURU","Bangalore",40,[
  cr("COMPUTER SCIENCE AND ENGG (AI AND MACHINE LEARNING)",  780,312,16,1,24,271,295),
  cr("COMPUTER SCIENCE AND ENGINEERING",                    2580,1032,51,1,78,902,980),
  cr("COMPUTER SCIENCE AND ENGINEERING (AI AND DATA SCIENCE)",240,96, 5,1, 7,83,90),
  cr("COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",      420,168, 8,1,13,146,159),
  cr("ELECTRICAL & ELECTRONICS ENGINEERING",                  60, 24, 1,0, 2,21,23),
  cr("ELECTRONICS AND COMMUNICATION ENGG",                   240, 96, 5,1, 7,83,90),
]),
col(21,"School of Planning and Architecture, University of Mysore",
    "2ND FLOOR, SENATE BHAVAN, MANASAGANGOTRI P.O., MYSORE","Mysuru",50,[
  cr("B.PLAN",40,20,1,0,1,18,19),
]),
# ── PAGE 116 ─────────────────────────────────────────────────────────────────
col(22,"Sharanbasava University (Exclusively for Women) (Formerly Goduati Engineering College For Women)",
    "SHARNBASVESHWARA INSTITUTIONS CAMPUS, KALABURAGI (GULBARGA)-585103, KARNATAKA","Kalaburagi",40,[
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",60,24,1,1,15, 7,22),
  cr("B TECH IN CIVIL ENGINEERING",                           30,12,1,0, 8, 3,11),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           150,60,3,1,39,17,56),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",        60,24,1,1,15, 7,22),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    120,48,2,1,32,13,45),
]),
col(23,"Sharanbasava University (Formerly Appa Institute of Engineering and Technology)",
    "SHARNBASVESHWARA INSTITUTIONS CAMPUS, KALABURAGI (GULBARGA)-585103, KARNATAKA","Kalaburagi",40,[
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",    60,24,1,1,15, 7,22),
  cr("B TECH IN CIVIL ENGINEERING",                          120,48,3,1,31,13,44),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           180,72,4,1,47,20,67),
  cr("B TECH IN ELECTRICAL & ELECTRONICS ENGINEERING",        60,24,1,0,16, 7,23),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",    120,48,3,1,31,13,44),
  cr("B TECH IN ENERGY ENGINEERING",                          60,24,1,0,16, 7,23),
  cr("B TECH IN MECHANICAL ENGINEERING",                     120,48,2,1,32,13,45),
  cr("BTECH IN COMPUTER SCIENCE AND DESIGN",                  60,24,1,0,16, 7,23),
]),
# ── PAGE 117 ─────────────────────────────────────────────────────────────────
col(24,"Srinivas University",
    "SRINIVAS CAMPUS MUKKA MANGALURU","Dakshina Kannada",40,[
  cr("B TECH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",120,48,2,1, 3,42,45),
  cr("B TECH IN CIVIL ENGINEERING",                           60,24,1,0, 2,21,23),
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           180,72,4,1, 5,62,67),
  cr("B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",     30,12,1,0, 1,10,11),
  cr("B TECH IN MECHANICAL ENGINEERING",                      60,24,1,1, 2,20,22),
  cr("COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",     60,24,1,1, 2,20,22),
]),
col(25,"THE CHANAKYA UNIVERSITY",
    "NO 29 HARALURU, DEVANAHALLI TALUK (NEAR BENGALURU INTERNATIONAL AIRPORT)","Bangalore",40,[
  cr("B TECH IN COMPUTER SCIENCE AND ENGINEERING",           120,48,2,1, 4,41,45),
  cr("B.Tech In BIOTECHNOLOGY & BIO-ENGINEERING",             60,24,1,0, 2,21,23),
  cr("B.TECH IN CIVIL CONSTRUCTION AND SUSTAINABILITY ENGINEERING",60,24,1,1,2,20,22),
  cr("B.TECH IN COMPUTER SCIENCE AND ARTIFICIAL INTELLIGENCE",120,48,3,1, 3,41,44),
  cr("B.TECH IN ELECTRICAL ENGINEERING AND COMPUTER SCIENCE",  60,24,1,1, 2,20,22),
  cr("B.TECH IN ELECTRONICS ENGINEERING (VLSI AND EMBEDDED SYSTEM)",120,48,3,1,3,41,44),
  cr("B.TECH IN MECHANICAL AND AEROSPACE ENGINEERING",         60,24,1,0, 2,21,23),
]),
# ── PAGE 118 (image) ─────────────────────────────────────────────────────────
col(26,"University of Mysuru",
    "B.N.BAHADUR INSTITUTE OF MANAGEMENT SCIENCES, MANASAGANGOTRI, HUNSUR ROAD, MYSORE","Mysuru",50,[
  cr("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",              60,30,2,0, 2,26,28),
  cr("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",          90,45,2,0, 4,39,43),
  cr("BIOMEDICAL AND ROBOTIC ENGINEERING",                    60,30,2,0, 2,26,28),
  cr("CIVIL ENVIRONMENTAL ENGINEERING",                       30,15,1,0, 1,13,14),
  cr("COMPUTER SCIENCE AND DESIGN",                          120,60,3,1, 5,51,56),
  cr("COMPUTER SCIENCE AND ENGINEERING",                      60,30,1,0, 2,27,29),
]),
col(27,"Vidyashilp University",
    "#125, BETTENAHALLI, KUNDANA HOBLI, CHAPPARKALLU RD, BENGALURU, KARNATAKA 562110","Bangalore",40,[
  cr("B TECH (HONS) COMPUTER SCIENCE AND ENGINEERING AND ENGINEERING (DATA SCIENCE)",120,48,2,1,4,41,45),
]),
]

d["colleges"].extend(ann_o)
with open("seat_matrix_data.json","w",encoding="utf-8") as f:
    json.dump(d,f,indent=2,ensure_ascii=False)

# ── Verification ──────────────────────────────────────────────────────────────
PDF_O = {"intake":33120,"kea":13294,"ph":665,"spl":142,"hk":1625,"rk":10862,"tot":12487}
LABS  = {"intake":"Total Intake","kea":"Total KEA","ph":"PH 5%","spl":"SPL",
         "hk":"HK","rk":"RK","tot":"TOT HK-RK"}

cols_o = [c for c in d["colleges"] if c["annexure"]=="O"]
s = {k:0 for k in PDF_O}
for c in cols_o:
    for cr_rec in c["courses"]:
        s["intake"] += cr_rec.get("total_intake",0)
        s["kea"]    += cr_rec.get("total_kea_seats",0)
        s["ph"]     += cr_rec.get("kea_ph",0)
        s["spl"]    += cr_rec.get("kea_spl",0)
        s["hk"]     += cr_rec.get("kea_hk",0)
        s["rk"]     += cr_rec.get("kea_rk",0)
        s["tot"]    += cr_rec.get("kea_tot",0)

sep="-"*68
print(sep)
print("  ANNEXURE O FINAL VERIFICATION vs PDF Grand Total")
print(sep)
all_ok=True
for k,pv in PDF_O.items():
    ov=s[k]; diff=ov-pv
    ok="OK" if diff==0 else f"OFF {diff:+d}"
    if diff!=0: all_ok=False
    print(f"  {LABS[k]:<22} {pv:>8} {ov:>8} {diff:>+8}  {ok}{'  <---' if diff!=0 else ''}")
print(sep)
print(f"  RESULT: {'PERFECT - ALL MATCH!' if all_ok else 'MISMATCHES'}")
print(f"  Colleges: {len(cols_o)}/27")

if not all_ok:
    # Per-college breakdown
    PDF_INS = {1:780,2:1910,3:1320,4:960,5:2640,6:1080,7:1980,8:960,9:630,
               10:420,11:1080,12:1800,13:1110,14:1800,15:1260,16:3420,17:180,
               18:2040,19:540,20:4320,21:40,22:420,23:780,24:510,25:600,26:420,27:120}
    print()
    for c in sorted(cols_o,key=lambda x:x["college_number"]):
        ours=sum(cr["total_intake"] for cr in c["courses"])
        pdf=PDF_INS.get(c["college_number"],0)
        diff=ours-pdf
        if diff!=0:
            print(f"  #{c['college_number']:>2} {c['college_name'][:48]:<48} PDF={pdf} Ours={ours} DIFF={diff:+d}")
