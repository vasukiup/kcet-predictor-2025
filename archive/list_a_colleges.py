"""
Check why standard Government / VTU Constituent Colleges have type counts of 22
but the user says they cannot see them in the app.
Let's print all 22 colleges in 'A' and their fields.
"""
import json

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

a_cols = [c for c in d["colleges"] if c["annexure"] == "A"]
print(f"Total Annexure A colleges: {len(a_cols)}")
for c in a_cols:
    print(f"Name: {c['college_name']} | Type: {c['college_type']} | Courses count: {len(c['courses'])}")
