"""
Compare college list in Annexure A baseline with standard names.
Let's see what is the college list in Annexure A of seat_matrix_data_v1_baseline.json,
and find out which college is #23.
"""
import json

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    d = json.load(f)

a_cols = [c for c in d["colleges"] if c["annexure"] == "A"]
print(f"Colleges in baseline Annexure A: {len(a_cols)}")
for c in a_cols:
    print(f"  #{c['college_number']} {c['college_name']}")
