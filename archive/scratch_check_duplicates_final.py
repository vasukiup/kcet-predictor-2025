import json

with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

has_duplicates = False
for col in db["colleges"]:
    seen = {}
    for c in col["courses"]:
        name = c["course_name"]
        seen[name] = seen.get(name, 0) + 1
    duplicates = [name for name, count in seen.items() if count > 1]
    if duplicates:
        has_duplicates = True
        print(f"College {col['college_number']} ({col['college_name']}) in Annexure {col['annexure']} has duplicate course names:")
        for name in duplicates:
            # Let's see details of the duplicate courses
            print(f"  - {name}")
            for c in col["courses"]:
                if c["course_name"] == name:
                    print(f"    intake={c['total_intake']}, KEA={c['total_kea_seats']}, sports={c.get('sports',0)}, ncc={c.get('ncc',0)}")

if not has_duplicates:
    print("SUCCESS: No duplicate courses found in the entire final database!")
