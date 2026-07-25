"""
Check the college type counts in the JSON before the merge.
Let's see what are the college types in the JSON baseline and what types are assigned after build_EV.py.
"""
import json, re

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    d_base = json.load(f)

print("Baseline colleges count:", len(d_base["colleges"]))
base_types = {}
for c in d_base["colleges"]:
    base_types[c["college_type"]] = base_types.get(c["college_type"], 0) + 1
print("Baseline types:", base_types)

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d_curr = json.load(f)

print("\nCurrent colleges count:", len(d_curr["colleges"]))
curr_types = {}
for c in d_curr["colleges"]:
    curr_types[c["college_type"]] = curr_types.get(c["college_type"], 0) + 1
print("Current types:", curr_types)

# Let's inspect Annexure A colleges in baseline
ann_a_names = [c["college_name"] for c in d_base["colleges"] if c["annexure"] == "A"]
print("\nAnnexure A colleges in baseline:")
for name in ann_a_names[:10]:
    print(" -", name)
