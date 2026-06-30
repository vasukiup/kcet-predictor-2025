import json

with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for col in db["colleges"]:
    if "b m s college of engineering" in col["college_name"].lower():
        print(f"College: '{col['college_name']}', Ann: {col.get('annexure')}")
        print("Courses:")
        for c in col["courses"]:
            print(f"  - '{c['course_name']}'")
