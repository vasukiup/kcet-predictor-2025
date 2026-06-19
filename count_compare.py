"""
Diagnose name normalization and trace what colleges are in the baseline before build_EV.py,
and compare with what is in seat_matrix_data_v1_baseline.json.
"""
import json, re

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    base = json.load(f)

# How many colleges in baseline by annexure?
counts = {}
for c in base["colleges"]:
    counts[c["annexure"]] = counts.get(c["annexure"], 0) + 1
print("Baseline counts in file:", counts)

with open("seat_matrix_data.json", encoding="utf-8") as f:
    curr = json.load(f)

# How many colleges in current seat_matrix_data.json by annexure?
curr_counts = {}
for c in curr["colleges"]:
    curr_counts[c["annexure"]] = curr_counts.get(c["annexure"], 0) + 1
print("Current counts in file:", curr_counts)
