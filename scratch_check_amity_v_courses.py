import json

with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for col in db["colleges"]:
    if col["college_name"] == "AMITY UNIVERSITY" and col["annexure"] == "V":
        print(f"College: '{col['college_name']}', Ann: {col.get('annexure')}")
        print(f"Total Intake: {col['total_intake']}")
        print(f"Total KEA Seats: {col['total_kea_seats']}")
        print("Courses:")
        for c in col["courses"]:
            print(f"  - '{c['course_name']}': intake={c.get('total_intake')}, KEA={c.get('total_kea_seats')}")
