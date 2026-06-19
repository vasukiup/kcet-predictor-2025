"""
Inspect which standard baseline colleges in A, B, C, D were replaced.
Also inspect university/deemed colleges in M, O, P, Z that were replaced.
"""
import json, re

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    d = json.load(f)

# Normalize name
def norm(name):
    n = name.upper()
    n = re.sub(r'\(AUTONOMOUS\)', '', n)
    n = re.sub(r'FORMERLY.*', '', n)
    n = re.sub(r'[^A-Z0-9]', '', n)
    return n

# Load current parsed E and V names from our parsed colleges
with open("seat_matrix_data.json", encoding="utf-8") as f:
    d_curr = json.load(f)

e_names = {norm(c["college_name"]) for c in d_curr["colleges"] if c["annexure"] == "E"}
v_names = {norm(c["college_name"]) for c in d_curr["colleges"] if c["annexure"] == "V"}

# Count replacements for A, B, C, D, M, O, P, Z
for ann in ["A", "B", "C", "D", "M", "O", "P", "Z"]:
    cols = [c for c in d["colleges"] if c["annexure"] == ann]
    replaced = []
    for c in cols:
        n = norm(c["college_name"])
        if (ann in ["A", "B", "C", "D"] and n in e_names) or (ann in ["M", "O", "P", "Z"] and n in v_names):
            replaced.append(c["college_name"])
    print(f"\nAnnexure {ann}: total={len(cols)}, replaced={len(replaced)}")
    for r in replaced:
        print("  -", r)
