import json, sys
sys.stdout.reconfigure(encoding="utf-8")
with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)
by_dist = d["stats"]["by_district"]
sorted_d = sorted(by_dist.items(), key=lambda x: -x[1]["total"])
other_count = by_dist.get("Other",{}).get("college_count",0)
print(f"Districts: {len(by_dist)}   |  'Other' colleges remaining: {other_count}")
print()
print(f"{'District':<22} {'Colleges':>8} {'Seats':>8}")
print("-"*42)
for dist, v in sorted_d[:20]:
    print(f"{dist:<22} {v['college_count']:>8} {v['total']:>8,}")
