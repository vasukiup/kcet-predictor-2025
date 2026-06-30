import json

with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for col in db["colleges"]:
    if "Sri Venkateshwara" in col["college_name"] or "Sri Venkateswara" in col["college_name"]:
        print(f"College: {col['college_name']} (Annexure: {col['annexure']})")
        for c in col["courses"]:
            print(f"  - {c['course_name']}: intake={c['total_intake']}, KEA={c['total_kea_seats']}, sports={c.get('sports', 0)}, ncc={c.get('ncc', 0)}, spl={c.get('kea_spl', 0)}")
