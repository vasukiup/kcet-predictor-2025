"""Show full addresses of colleges still needing district mapping."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Colleges where address is incomplete — need full address
check = {24, 127}  # BASAV and Sri Basaveswara

for c in d["colleges"]:
    if c["college_number"] in check and c["annexure"] == "C":
        print(f"#{c['college_number']} {c['college_name']}")
        print(f"  Address: {c.get('address','')}")
        print()
