"""
Add missing Annexure A college #23: VTU CPGS Mysuru
Data read from user-provided image.
"""
import json

with open("seat_matrix_data.json", encoding="utf-8") as f:
    data = json.load(f)

new_college = {
    "college_number": 23,
    "college_name": "Visvesvaraya Technological University, VTU, CPGS, Mysuru",
    "address": "Mysuru",
    "annexure": "A",
    "college_type": "Government / VTU Constituent Colleges",
    "district": "Mysore",
    "cat1_pct": 100,
    "cat2_pct": 0,
    "cat3_pct": 0,
    "total_intake": 300,
    "total_kea_seats": 300,
    "courses": [
        {
            "course_name": "B TECH IN ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",
            "total_intake": 60,
            "total_kea_seats": 60,
            "snq_5pct": 3,
            "kea_ph": 3,
            "kea_spl": 1,
            "kea_hk": 5,
            "kea_rk": 51,
            "kea_tot": 56,
            "over_above_5pct": 3,
            "cat2_seats": 0,
            "cat3_seats": 0,
            "cat1_govt_pct": 100,
            "cat2_pct": 0,
            "cat3_pct": 0
        },
        {
            "course_name": "B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",
            "total_intake": 60,
            "total_kea_seats": 60,
            "snq_5pct": 3,
            "kea_ph": 3,
            "kea_spl": 1,
            "kea_hk": 4,
            "kea_rk": 52,
            "kea_tot": 56,
            "over_above_5pct": 3,
            "cat2_seats": 0,
            "cat3_seats": 0,
            "cat1_govt_pct": 100,
            "cat2_pct": 0,
            "cat3_pct": 0
        },
        {
            "course_name": "COMPUTER SCIENCE AND ENGINEERING",
            "total_intake": 120,
            "total_kea_seats": 120,
            "snq_5pct": 6,
            "kea_ph": 6,
            "kea_spl": 1,
            "kea_hk": 9,
            "kea_rk": 104,
            "kea_tot": 113,
            "over_above_5pct": 6,
            "cat2_seats": 0,
            "cat3_seats": 0,
            "cat1_govt_pct": 100,
            "cat2_pct": 0,
            "cat3_pct": 0
        },
        {
            "course_name": "MECHANICAL ENGINEERING",
            "total_intake": 60,
            "total_kea_seats": 60,
            "snq_5pct": 3,
            "kea_ph": 3,
            "kea_spl": 1,
            "kea_hk": 4,
            "kea_rk": 52,
            "kea_tot": 56,
            "over_above_5pct": 3,
            "cat2_seats": 0,
            "cat3_seats": 0,
            "cat1_govt_pct": 100,
            "cat2_pct": 0,
            "cat3_pct": 0
        }
    ]
}

# Check it's not already in there
existing = [c for c in data["colleges"] if "CPGS" in c["college_name"] and "Mysuru" in c["college_name"]]
if existing:
    print("Already exists:", existing[0]["college_name"])
else:
    data["colleges"].append(new_college)

    # Update stats
    a_colleges = [c for c in data["colleges"] if c["annexure"] == "A"]
    data["stats"]["by_annexure"]["A"]["colleges"] = len(a_colleges)
    data["stats"]["by_annexure"]["A"]["total_seats"] = sum(c["total_intake"] for c in a_colleges)
    data["stats"]["by_annexure"]["A"]["kea_seats"]   = sum(c["total_kea_seats"] for c in a_colleges)
    data["stats"]["total_colleges"] = len(data["colleges"])
    data["stats"]["total_seats"]    = sum(c["total_intake"] for c in data["colleges"])
    data["stats"]["total_kea_seats"] = sum(c["total_kea_seats"] for c in data["colleges"])
    data["metadata"]["total_colleges"] = len(data["colleges"])

    # Update district stats
    data["stats"]["by_district"]["Mysore"] = data["stats"]["by_district"].get("Mysore", {"total": 0, "kea": 0, "colleges": 0})
    data["stats"]["by_district"]["Mysore"]["total"]    += 300
    data["stats"]["by_district"]["Mysore"]["kea"]      += 300
    data["stats"]["by_district"]["Mysore"]["colleges"] += 1

    # Update course stats
    for course in new_college["courses"]:
        cn = course["course_name"]
        if cn not in data["stats"]["by_course"]:
            data["stats"]["by_course"][cn] = {"total": 0, "kea": 0, "colleges": 0}
        data["stats"]["by_course"][cn]["total"]    += course["total_intake"]
        data["stats"]["by_course"][cn]["kea"]      += course["total_kea_seats"]
        data["stats"]["by_course"][cn]["colleges"] += 1

    # Update all_courses
    new_courses = [c["course_name"] for c in new_college["courses"]]
    for cn in new_courses:
        if cn not in data["all_courses"]:
            data["all_courses"].append(cn)
            data["all_courses"].sort()
            data["metadata"]["total_courses_offered"] = len(data["all_courses"])

    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Added: Visvesvaraya Technological University, VTU, CPGS, Mysuru")
    print(f"Annexure A now has {len(a_colleges)} colleges (target: 23)")
    print(f"Total colleges: {len(data['colleges'])}")
    print(f"Total seats: {data['stats']['total_seats']:,}")

    # Verify internal consistency for this college
    summed = sum(c["total_intake"] for c in new_college["courses"])
    print(f"\nConsistency check: total_intake={new_college['total_intake']}, sum of courses={summed} -> {'OK' if summed == new_college['total_intake'] else 'MISMATCH'}")
