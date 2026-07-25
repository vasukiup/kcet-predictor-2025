import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    v1 = json.load(f)
with open("seat_matrix_data.json", encoding="utf-8") as f:
    v2 = json.load(f)

print("=== v1 Annexure D colleges (claimed 42 vs PDF ground truth 25) ===")
d_cols = [c for c in v1["colleges"] if c["annexure"] == "D"]
print(f"Total D in v1: {len(d_cols)}")
for c in sorted(d_cols, key=lambda x: x.get("college_number", 999)):
    num = c.get("college_number", "?")
    name = c["college_name"][:55]
    courses = len(c["courses"])
    intake = c.get("total_intake", 0)
    print(f"  #{num:>3} {name:<55} | courses={courses} | intake={intake}")

print()
print("=== v1 Annexure A colleges (claimed 22 vs PDF ground truth 22) ===")
a_cols = [c for c in v1["colleges"] if c["annexure"] == "A"]
print(f"Total A in v1: {len(a_cols)}")
for c in sorted(a_cols, key=lambda x: x.get("college_number", 999)):
    num = c.get("college_number", "?")
    name = c["college_name"][:55]
    courses = len(c["courses"])
    intake = c.get("total_intake", 0)
    print(f"  #{num:>3} {name:<55} | courses={courses} | intake={intake}")

print()
print("=== v1 Annexure B colleges (claimed 6 vs PDF ground truth 8) ===")
b_cols = [c for c in v1["colleges"] if c["annexure"] == "B"]
print(f"Total B in v1: {len(b_cols)}")
for c in sorted(b_cols, key=lambda x: x.get("college_number", 999)):
    num = c.get("college_number", "?")
    name = c["college_name"][:55]
    courses = len(c["courses"])
    intake = c.get("total_intake", 0)
    print(f"  #{num:>3} {name:<55} | courses={courses} | intake={intake}")

print()
print("=== v1 intake mismatches in D ===")
for c in d_cols:
    claimed = c.get("total_intake", 0)
    summed = sum(x.get("total_intake", 0) for x in c.get("courses", []))
    if claimed > 0 and abs(claimed - summed) > 5:
        print(f"  {c['college_name'][:50]}: claimed={claimed}, sum={summed}, diff={claimed-summed}")
