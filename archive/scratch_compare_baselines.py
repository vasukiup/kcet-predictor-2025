import json

with open("seat_matrix_data_v1_baseline.json", "r", encoding="utf-8") as f:
    orig = json.load(f)

# Run extract_seats_v2 build_output
from extract_seats_v2 import extract_all, build_output
colleges = extract_all()
new_output = build_output(colleges)

print("Original stats:")
print(f"  Colleges: {len(orig['colleges'])}")
print(f"  Seats: {sum(c.get('total_intake', 0) for c in orig['colleges'])}")
print(f"  KEA: {sum(c.get('total_kea_seats', 0) for c in orig['colleges'])}")

print("\nNew stats:")
print(f"  Colleges: {len(new_output['colleges'])}")
print(f"  Seats: {sum(c.get('total_intake', 0) for c in new_output['colleges'])}")
print(f"  KEA: {sum(c.get('total_kea_seats', 0) for c in new_output['colleges'])}")

# Check if SVCE courses changed
for c in orig["colleges"]:
    if c["college_number"] == 134 and c["annexure"] == "C":
        print("\nOriginal SVCE courses:")
        for cr in c["courses"]:
            print(f"  - {cr['course_name']}: intake={cr['total_intake']}")

for c in new_output["colleges"]:
    if c["college_number"] == 134 and c["annexure"] == "C":
        print("\nNew SVCE courses:")
        for cr in c["courses"]:
            print(f"  - {cr['course_name']}: intake={cr['total_intake']}")
