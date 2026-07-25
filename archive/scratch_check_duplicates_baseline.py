import json

with open("seat_matrix_data_v1_baseline.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for col in db["colleges"]:
    seen = {}
    for c in col["courses"]:
        name = c["course_name"]
        seen[name] = seen.get(name, 0) + 1
    duplicates = [name for name, count in seen.items() if count > 1]
    if duplicates:
        print(f"College {col['college_number']} ({col['college_name']}) in Annexure {col['annexure']} has duplicate course names:")
        for name in duplicates:
            print(f"  - {name}")
