"""
Trace what happens to the 22 government colleges.
Let's print their names and see why they are not in the new_colleges list
at the end of merge_revisions.py.
"""
import json, re

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Print all college counts by annexure and college_type
types = {}
for c in d["colleges"]:
    key = (c["annexure"], c.get("college_type", "None"))
    types[key] = types.get(key, 0) + 1

print("Annexure/Type counts in current seat_matrix_data.json:")
for k, count in sorted(types.items()):
    print(f"  {k}: {count}")
