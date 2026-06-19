"""
List all colleges with district = "Other" or missing district,
showing their address so we can map them correctly.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

others = [c for c in d["colleges"] if not c.get("district") or c["district"] in ("Other","other","")]
others.sort(key=lambda x: (x["annexure"], x["college_number"]))

print(f"Total colleges with 'Other'/missing district: {len(others)}\n")
print(f"{'#':>4} {'Ann':>4}  {'District':>10}  {'College':<40}  Address")
print("-"*130)
for c in others:
    addr = c.get("address","")[:60]
    print(f"{c['college_number']:>4} {c['annexure']:>4}  {c.get('district',''):>10}  {c['college_name'][:40]:<40}  {addr}")
