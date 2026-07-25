import json

with open("seat_matrix_data_v1_baseline.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for col in db["colleges"]:
    if "T.John" in col["college_name"] or "T. John" in col["college_name"]:
        print(col["college_name"])
        for c in col["courses"]:
            print(f"  - {c['course_name']} (Intake: {c['total_intake']})")
