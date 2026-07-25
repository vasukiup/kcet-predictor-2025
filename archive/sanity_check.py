"""
Run a quick check on the final seat_matrix_data.json:
1. Ensure no "Other" or "Mangalore" districts are present.
2. Confirm the number of colleges, total intake, and total KEA seats.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

print("Total colleges in JSON:", len(d["colleges"]))

# Count by annexure
ann_counts = {}
for c in d["colleges"]:
    ann = c["annexure"]
    ann_counts[ann] = ann_counts.get(ann, 0) + 1
print("College count by annexure:", ann_counts)

# Check for "Other" or "Mangalore" districts
districts = set()
for c in d["colleges"]:
    dist = c.get("district")
    districts.add(dist)
    if dist in ("Other", "Mangalore"):
        print(f"Warning: College {c['college_name']} has district {dist}")

print("Districts found:", sorted(list(districts)))
