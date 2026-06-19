"""
Check for duplicate seat matrices (colleges/courses) across different Annexures.
We will inspect if any college has duplicate courses or if the same college appears in multiple annexures,
and if so, check if the course allocations are identical or represent distinct allocations.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

colleges = d["colleges"]

# 1. Check if same college (by name) is present in multiple annexures
name_to_annexures = {}
for c in colleges:
    name = c["college_name"].strip().upper()
    ann = c["annexure"]
    if name not in name_to_annexures:
        name_to_annexures[name] = []
    name_to_annexures[name].append((ann, c["college_number"]))

duplicates = {name: anns for name, anns in name_to_annexures.items() if len(anns) > 1}

print(f"Total unique college names: {len(name_to_annexures)}")
print(f"Colleges appearing in multiple annexures: {len(duplicates)}")
print("="*80)

for name, anns in sorted(duplicates.items())[:20]:
    print(f"\nCollege: {name}")
    print(f"  Appears in: {', '.join(f'Annexure {a} (Col #{num})' for a, num in anns)}")
    
    # Let's inspect the courses of this college in each annexure
    for a, num in anns:
        col_data = next(c for c in colleges if c["annexure"] == a and c["college_number"] == num)
        print(f"  --- Annexure {a} ---")
        print(f"    Total Intake: {col_data['total_intake']} | KEA Seats: {col_data['total_kea_seats']}")
        print(f"    Courses ({len(col_data['courses'])}):")
        for cr in col_data["courses"][:5]:
            print(f"      - {cr['course_name']}: Intake={cr['total_intake']}, KEA={cr['total_kea_seats']}")
        if len(col_data["courses"]) > 5:
            print(f"      ... and {len(col_data['courses'])-5} more courses")

if len(duplicates) > 20:
    print(f"\n... and {len(duplicates)-20} more duplicate colleges")
