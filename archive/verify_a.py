import json, sys
sys.stdout.reconfigure(encoding="utf-8")
with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)
a = sorted([c for c in d["colleges"] if c["annexure"] == "A"], key=lambda x: x["college_number"])
print(f"Annexure A: {len(a)}/23 colleges")
for col in a:
    num = col["college_number"]
    name = col["college_name"][:60]
    intake = col["total_intake"]
    courses = len(col["courses"])
    print(f"  #{num:>2} {name:<60} | intake={intake:>4} | courses={courses}")
print(f"\nTotal A seats: {sum(c['total_intake'] for c in a):,}")
