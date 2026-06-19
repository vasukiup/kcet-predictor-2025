"""
Diagnose why Annexure A colleges are missing after merge.
We will print names of colleges in A, and print their norm() values.
Then print names of colleges in E and their norm() values, and see if there are false overlaps.
"""
import json, re

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

colleges = d["colleges"]

def norm(name):
    n = name.upper()
    n = re.sub(r'\(AUTONOMOUS\)', '', n)
    n = re.sub(r'FORMERLY.*', '', n)
    n = re.sub(r'[^A-Z0-9]', '', n)
    return n

a_cols = [c for c in colleges if c["annexure"] == "A"]
e_cols = [c for c in colleges if c["annexure"] == "E"]

print(f"Colleges in A: {len(a_cols)}")
print(f"Colleges in E: {len(e_cols)}")

a_norms = {norm(c["college_name"]): c["college_name"] for c in a_cols}
e_norms = {norm(c["college_name"]): c["college_name"] for c in e_cols}

overlap = set(a_norms.keys()) & set(e_norms.keys())
print(f"\nOverlap count between A and E: {len(overlap)}")
for o in sorted(list(overlap)):
    print(f"  Norm key: {o}")
    print(f"    In A: {a_norms[o]}")
    print(f"    In E: {e_norms[o]}")
