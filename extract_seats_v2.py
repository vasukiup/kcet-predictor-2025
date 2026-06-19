"""
Karnataka Engineering Seat Matrix - IMPROVED Extractor v2
Fix: Properly stitch multi-page colleges by tracking active college
     across page boundaries within the same annexure.
"""
import pdfplumber
import json
import re
from collections import defaultdict

PDF_PATH = "Seat_Matrix_05072025.pdf"

ANNEXURE_LABELS = {
    "A": "Government / VTU Constituent Colleges",
    "B": "Government Aided Private Colleges",
    "C": "Private Unaided Colleges",
    "D": "Private Unaided Minority Colleges",
}

ANNEXURE_QUOTA = {
    "A": {"cat1_pct": 100, "cat2_pct": 0,  "cat3_pct": 0},
    "B": {"cat1_pct": 95,  "cat2_pct": 0,  "cat3_pct": 5},
    "C": {"cat1_pct": 45,  "cat2_pct": 30, "cat3_pct": 25},
    "D": {"cat1_pct": 40,  "cat2_pct": 30, "cat3_pct": 30},
}

# ─────────────────────────────────────────────────────────
# Helper: detect which annexure a page belongs to
# ─────────────────────────────────────────────────────────
def detect_annexure_on_page(text):
    for ann in ["A", "B", "C", "D", "E"]:
        if f"ANNEXURE : {ann}" in text:
            return ann
    return None

# ─────────────────────────────────────────────────────────
# Helper: parse course rows from a block of text lines
# Returns list of course dicts
# ─────────────────────────────────────────────────────────
def parse_course_rows(lines, annexure):
    courses = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Match: "N COURSE NAME ... numbers"
        # Course number at start, then name (can be multi-word), then digits
        m = re.match(r'^(\d{1,3})\s+([A-Z][A-Z0-9\s&()\-\'/,\.]+?)\s+(\d{2,4})\s+(\d{2,4})', line)
        if not m:
            # Some course names wrap to next line — try joining with next line
            if i + 1 < len(lines):
                combined = line + " " + lines[i+1].strip()
                m = re.match(r'^(\d{1,3})\s+([A-Z][A-Z0-9\s&()\-\'/,\.]+?)\s+(\d{2,4})\s+(\d{2,4})', combined)
                if m:
                    line = combined
                    i += 1  # consumed next line too
        
        if m:
            course_name = m.group(2).strip()
            # Skip if it looks like a page number or total line
            if re.match(r'^(Ins Total|TOTAL|Page|TOT)', course_name, re.IGNORECASE):
                i += 1
                continue

            rest = line[m.start(3):]
            nums = re.findall(r'\d+', rest)

            if len(nums) >= 2:
                total_intake = int(nums[0])
                total_kea = int(nums[1])

                # Sanity check - intakes should be reasonable
                if total_intake > 5000 or total_intake < 10:
                    i += 1
                    continue

                course = {
                    "course_name": course_name,
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

                # For private colleges, cat2 and cat3 appear after kea_tot
                if annexure in ["C", "D"] and len(nums) >= 10:
                    course["cat2_seats"] = int(nums[8])
                    course["cat3_seats"] = int(nums[9])
                    course["over_above"] = int(nums[10]) if len(nums) > 10 else 0

                courses.append(course)

        i += 1
    return courses

# ─────────────────────────────────────────────────────────
# Helper: extract Ins Total line from text
# Returns (total_intake, total_kea) or None
# ─────────────────────────────────────────────────────────
def parse_ins_total(lines):
    for line in lines:
        line = line.strip()
        if re.match(r'^Ins\s+Total', line, re.IGNORECASE):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                return int(nums[0]), int(nums[1])
    return None, None

# ─────────────────────────────────────────────────────────
# Helper: check if a line is a new college header
# Returns (serial_num, college_name) or None
# ─────────────────────────────────────────────────────────
def is_college_header(lines, idx):
    line = lines[idx].strip()
    m = re.match(r'^(\d+)\s+(.+)$', line)
    if not m:
        return None
    num = int(m.group(1))
    name = m.group(2).strip()
    # Must be followed (within 3 lines) by "Address :"
    for k in range(idx+1, min(idx+4, len(lines))):
        if lines[k].strip().startswith("Address"):
            return num, name
        # name can wrap to next line
        if lines[k].strip() and not lines[k].strip().startswith("Address") and not re.match(r'^Sl', lines[k].strip()):
            name += " " + lines[k].strip()
    # Check again
    for k in range(idx+1, min(idx+4, len(lines))):
        if lines[k].strip().startswith("Address"):
            return num, name
    return None

# ─────────────────────────────────────────────────────────
# Main extraction — page-by-page, with cross-page stitching
# ─────────────────────────────────────────────────────────
def extract_all():
    current_annexure = None
    current_college  = None   # dict being built
    finalized        = []     # completed colleges

    def finalize_college(college):
        if college:
            finalized.append(college)

    print("Extracting (v2 with multi-page stitching)...")

    with pdfplumber.open(PDF_PATH) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}\n")

        for pg_idx, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # ── Detect annexure change ──────────────────
            ann_on_page = detect_annexure_on_page(text)
            if ann_on_page == "E":
                # Annexure E is a different format (detailed category breakdown)
                # Finalize any open college and skip
                if current_college:
                    finalize_college(current_college)
                    current_college = None
                current_annexure = "E"
                continue

            if ann_on_page and ann_on_page != current_annexure:
                # Entering a new annexure — finalize last college of old annexure
                if current_college and current_college.get("annexure") != ann_on_page:
                    finalize_college(current_college)
                    current_college = None
                current_annexure = ann_on_page

            if current_annexure not in ["A", "B", "C", "D"]:
                continue

            # ── Parse this page ─────────────────────────
            lines = text.splitlines()

            i = 0
            page_course_lines = []  # collect lines that belong to courses

            while i < len(lines):
                line = lines[i].strip()

                # Skip header/boilerplate lines
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

                # ── Detect college header ────────────────
                result = is_college_header(lines, i)
                if result:
                    serial_num, name = result

                    # Finalize previous college if this is a NEW one
                    if current_college:
                        # Parse any courses collected so far for previous college
                        extra = parse_course_rows(page_course_lines, current_annexure)
                        current_college["courses"].extend(extra)
                        page_course_lines = []
                        finalize_college(current_college)

                    # Read address from next line(s)
                    address = ""
                    for k in range(i+1, min(i+5, len(lines))):
                        l = lines[k].strip()
                        if l.startswith("Address"):
                            address = l.replace("Address :", "").strip()
                            break
                        elif l and not re.match(r'^Sl', l):
                            name += " " + l  # name continuation

                    quota = ANNEXURE_QUOTA.get(current_annexure, {})
                    current_college = {
                        "college_number":  serial_num,
                        "college_name":    name.strip(),
                        "address":         address,
                        "annexure":        current_annexure,
                        "college_type":    ANNEXURE_LABELS.get(current_annexure, ""),
                        "courses":         [],
                        "total_intake":    0,
                        "total_kea_seats": 0,
                        **quota,
                    }
                    i += 2
                    continue

                # ── Detect Ins Total ──────────────────────
                if re.match(r'^Ins\s+Total', line, re.IGNORECASE):
                    nums = re.findall(r'\d+', line)
                    if current_college and len(nums) >= 2:
                        # Only update if this is larger than what we have
                        # (handles case where multi-page college has partial total on earlier page)
                        t, k = int(nums[0]), int(nums[1])
                        if t > current_college["total_intake"]:
                            current_college["total_intake"] = t
                            current_college["total_kea_seats"] = k
                    i += 1
                    continue

                # ── Accumulate course candidate lines ────
                if current_college and re.match(r'^\d+\s+[A-Z]', line):
                    page_course_lines.append(line)
                    # Also grab next line in case name wraps
                    if i + 1 < len(lines) and lines[i+1].strip() and not re.match(r'^\d+\s', lines[i+1]):
                        page_course_lines.append(lines[i+1].strip())

                i += 1

            # ── End of page: parse any remaining course lines ──
            if current_college and page_course_lines:
                extra = parse_course_rows(page_course_lines, current_annexure)
                current_college["courses"].extend(extra)
                page_course_lines = []

        # Finalize last college
        if current_college:
            finalize_college(current_college)

    return finalized


# ─────────────────────────────────────────────────────────
# Post-processing
# ─────────────────────────────────────────────────────────
DISTRICT_MAP = {
    "BENGALURU": "Bangalore", "BANGALORE": "Bangalore",
    "MYSURU": "Mysore", "MYSORE": "Mysore",
    "MANGALURU": "Mangalore", "MANGALORE": "Mangalore",
    "BELAGAVI": "Belagavi", "BELGAUM": "Belagavi",
    "BALLARI": "Ballari", "BELLARY": "Ballari",
    "KALABURAGI": "Kalaburagi", "GULBARGA": "Kalaburagi",
    "VIJAYAPURA": "Vijayapura", "BIJAPUR": "Vijayapura",
    "SHIVAMOGGA": "Shivamogga", "SHIMOGA": "Shivamogga",
    "TUMAKURU": "Tumakuru", "TUMKUR": "Tumakuru",
    "DAVANAGERE": "Davanagere", "DAVANGERE": "Davanagere", "DAVENGERE": "Davanagere",
    "HASSAN": "Hassan",
    "DHARWAD": "Dharwad", "HUBLI": "Dharwad",
    "UDUPI": "Udupi",
    "DAKSHINA KANNADA": "Dakshina Kannada",
    "UTTARA KANNADA": "Uttara Kannada",
    "CHIKMAGALUR": "Chikmagalur", "CHIKKAMAGALURU": "Chikmagalur",
    "KODAGU": "Kodagu", "COORG": "Kodagu", "MADIKERI": "Kodagu",
    "MANDYA": "Mandya",
    "KOLAR": "Kolar",
    "CHIKKABALLAPURA": "Chikkaballapura", "CHIKBALLAPURA": "Chikkaballapura",
    "RAMANAGARA": "Ramanagara", "RAMANAGAR": "Ramanagara",
    "CHITRADURGA": "Chitradurga",
    "BAGALKOT": "Bagalkot", "BAGALKOTE": "Bagalkot",
    "BIDAR": "Bidar",
    "RAICHUR": "Raichur",
    "KOPPAL": "Koppal",
    "GADAG": "Gadag",
    "HAVERI": "Haveri",
    "YADGIR": "Yadgir",
    "CHAMARAJANAGARA": "Chamarajanagara", "CHAMARAJANAGAR": "Chamarajanagara",
    "KUSHALANAGAR": "Kodagu",
    "NARAGUND": "Gadag",
    "MUDDENAHALLI": "Chikkaballapura",
    "CHINTAMANI": "Chikkaballapura",
    "ARASIKERE": "Hassan",
    "CHALLAKERE": "Chitradurga",
    "BANTWAL": "Dakshina Kannada",
    "PUTTUR": "Dakshina Kannada",
    "MOODBIDRI": "Dakshina Kannada",
    "SULLIA": "Dakshina Kannada",
    "KARWAR": "Uttara Kannada",
    "SIRSI": "Uttara Kannada",
    "KUNDAPUR": "Udupi",
    "BRAHMAVAR": "Udupi",
    "BYNDOOR": "Udupi",
    "SHRAVANABELAGOLA": "Hassan",
    "SAKLESHPUR": "Hassan",
    "ARSIKERE": "Hassan",
    "HOLENARASIPURA": "Hassan",
    "TIPTUR": "Tumakuru",
    "GUBBI": "Tumakuru",
    "SIRA": "Tumakuru",
    "MADHUGIRI": "Tumakuru",
    "KANAKAPURA": "Ramanagara",
    "BIDADI": "Ramanagara",
    "CHANNAPATNA": "Ramanagara",
    "HOSKOTE": "Bangalore",
    "DEVANAHALLI": "Bangalore",
    "DODDABALLAPUR": "Bangalore",
    "NELAMANGALA": "Bangalore",
    "ANEKAL": "Bangalore",
    "NANJANGUD": "Mysore",
    "HUNSUR": "Mysore",
    "PIRIYAPATNA": "Mysore",
    "PERIYAPATNA": "Mysore",
    "PANDAVAPURA": "Mandya",
    "MADDUR": "Mandya",
    "SRIRANGAPATNA": "Mandya",
    "KRISHNARAJAPETE": "Mandya",
    "MALUR": "Kolar",
    "MULBAGAL": "Kolar",
    "BANGARPET": "Kolar",
    "HOSUR": "Kolar",
    "ROBERTSONPET": "Kolar",
    "SRINIVASPUR": "Kolar",
    "PAVAGADA": "Tumakuru",
    "HIRIYUR": "Chitradurga",
    "HOLALKERE": "Chitradurga",
    "HOSADURGA": "Chitradurga",
    "DAVANAGERE": "Davanagere",
    "HARIHAR": "Davanagere",
    "CHANNAGIRI": "Davanagere",
    "SHIKARIPURA": "Shivamogga",
    "BHADRAVATI": "Shivamogga",
    "SAGAR": "Shivamogga",
    "SORABA": "Shivamogga",
    "THIRTHAHALLI": "Shivamogga",
    "RON": "Gadag",
    "MUNDARGI": "Gadag",
    "SHIRHATTI": "Gadag",
    "RANIBENNUR": "Haveri",
    "BYADGI": "Haveri",
    "SAVANUR": "Haveri",
    "HANGAL": "Haveri",
    "HIREKERUR": "Haveri",
    "KUNDGOL": "Dharwad",
    "KALGHATGI": "Dharwad",
    "ANNIGERI": "Dharwad",
    "DHARWAD": "Dharwad",
    "MUDHOL": "Bagalkot",
    "HUNGUND": "Bagalkot",
    "BADAMI": "Bagalkot",
    "JAMKHANDI": "Bagalkot",
    "ILKAL": "Bagalkot",
    "SINDAGI": "Vijayapura",
    "MUDDEBIHAL": "Vijayapura",
    "BASAVAN BAGEWADI": "Vijayapura",
    "INDI": "Vijayapura",
    "SHAHAPUR": "Yadgir",
    "SURPUR": "Yadgir",
    "LINGASUGUR": "Raichur",
    "MANVI": "Raichur",
    "DEVADURGA": "Raichur",
    "SINDHANUR": "Raichur",
    "GANGAVATHI": "Koppal",
    "YELBARGA": "Koppal",
    "KUSHTAGI": "Koppal",
    "BHALKI": "Bidar",
    "HUMANABAD": "Bidar",
    "BASAVAKALYAN": "Bidar",
    "AURAD": "Bidar",
    "ALAND": "Kalaburagi",
    "AFZALPUR": "Kalaburagi",
    "CHINCHOLI": "Kalaburagi",
    "SHORAPUR": "Yadgir",
}

def get_district(address):
    addr_upper = address.upper()
    for keyword, district in DISTRICT_MAP.items():
        if keyword in addr_upper:
            return district
    return "Other"

def deduplicate_courses(courses):
    """Remove exact duplicate course entries (same name + intake)"""
    seen = set()
    result = []
    for c in courses:
        key = (c["course_name"], c["total_intake"])
        if key not in seen:
            seen.add(key)
            result.append(c)
    return result


# ─────────────────────────────────────────────────────────
# Build output JSON
# ─────────────────────────────────────────────────────────
def build_output(colleges):
    # Add district
    for c in colleges:
        c["district"] = get_district(c.get("address", ""))

    # Deduplicate courses per college
    for c in colleges:
        c["courses"] = deduplicate_courses(c["courses"])

    # Fill missing total_intake / total_kea_seats from course sums
    for c in colleges:
        if c["total_intake"] == 0 and c["courses"]:
            c["total_intake"] = sum(x["total_intake"] for x in c["courses"])
            c["total_kea_seats"] = sum(x["total_kea_seats"] for x in c["courses"])

    # All unique courses
    all_courses = sorted(set(cr["course_name"] for col in colleges for cr in col["courses"]))

    # Districts
    districts = sorted(set(c["district"] for c in colleges))

    # Stats
    from collections import Counter
    stats = {
        "total_colleges": len(colleges),
        "total_courses": len(all_courses),
        "by_annexure": {},
        "total_seats": sum(c["total_intake"] for c in colleges),
        "total_kea_seats": sum(c["total_kea_seats"] for c in colleges),
        "by_district": {},
        "by_course": {},
    }

    ann_labels = {"A": "Government", "B": "Government Aided", "C": "Private Unaided", "D": "Private Minority"}
    for ann in ["A", "B", "C", "D"]:
        grp = [c for c in colleges if c["annexure"] == ann]
        stats["by_annexure"][ann] = {
            "label": ann_labels[ann],
            "colleges": len(grp),
            "total_seats": sum(c["total_intake"] for c in grp),
            "kea_seats": sum(c["total_kea_seats"] for c in grp),
        }

    from collections import defaultdict
    dist_map = defaultdict(lambda: {"total": 0, "kea": 0, "colleges": 0})
    for col in colleges:
        d = col["district"]
        dist_map[d]["total"] += col["total_intake"]
        dist_map[d]["kea"] += col["total_kea_seats"]
        dist_map[d]["colleges"] += 1
    stats["by_district"] = dict(dist_map)

    course_map = defaultdict(lambda: {"total": 0, "kea": 0, "colleges": 0})
    for col in colleges:
        for cr in col["courses"]:
            n = cr["course_name"]
            course_map[n]["total"] += cr["total_intake"]
            course_map[n]["kea"] += cr["total_kea_seats"]
            course_map[n]["colleges"] += 1
    stats["by_course"] = dict(course_map)

    return {
        "metadata": {
            "notification": "ED 170 TEC 2025",
            "date": "05-07-2025",
            "version": "v2",
            "total_colleges": len(colleges),
            "total_courses_offered": len(all_courses),
            "annexures": {
                "A": "Government / VTU Constituent Colleges (100% KEA)",
                "B": "Government Aided Private Colleges (95% KEA)",
                "C": "Private Unaided Colleges (45% KEA / 30% COMEDK / 25% Mgmt)",
                "D": "Private Unaided Minority Colleges (40% KEA / 30% COMEDK / 30% Mgmt)",
            },
        },
        "colleges": colleges,
        "all_courses": all_courses,
        "districts": districts,
        "stats": stats,
    }


# ─────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    colleges = extract_all()
    output = build_output(colleges)

    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    s = output["stats"]
    print("=" * 60)
    print("EXTRACTION v2 COMPLETE")
    print("=" * 60)
    print(f"Total colleges : {s['total_colleges']}")
    print(f"Total seats    : {s['total_seats']:,}")
    print(f"Total KEA seats: {s['total_kea_seats']:,}")
    print(f"Unique courses : {s['total_courses']}")
    print()
    print("By Annexure:")
    for ann, info in s["by_annexure"].items():
        print(f"  [{ann}] {info['label']:<35} {info['colleges']:>4} colleges | {info['total_seats']:>7,} seats | {info['kea_seats']:>7,} KEA")
    print()
    print("Saved to seat_matrix_data.json")
