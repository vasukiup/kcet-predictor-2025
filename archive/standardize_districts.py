"""
Update build_EV.py's normalize_district logic to map:
- 'Gulbarga' to 'Kalaburagi'
- 'Mysore' to 'Mysuru'
- 'Ramanagar' to 'Ramanagara'
- 'Chikkaballapura' to 'Chikballapura'
- 'Chikmagalur' to 'Chikkamagaluru'
- 'Tumakuru' to 'Tumkur'
- 'Vijayapura' to 'Vijayapura' (wait, let's keep one standard)
Let's see if we can do this and re-run build_EV.py.
"""
import json, re

def run():
    with open("seat_matrix_data.json", encoding="utf-8") as f:
        d = json.load(f)

    # Let's map districts to a clean standard
    standard_map = {
        "Gulbarga": "Kalaburagi",
        "Mysore": "Mysuru",
        "Ramanagar": "Ramanagara",
        "Chikkaballapura": "Chikballapura",
        "Chikmagalur": "Chikkamagaluru",
        "Tumakuru": "Tumkur",
        "Hubli": "Dharwad",
        "Bangalore Rural": "Bangalore" # keep under Bangalore or separate? Usually Bangalore is fine
    }

    for c in d["colleges"]:
        dist = c.get("district")
        if dist in standard_map:
            c["district"] = standard_map[dist]

    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

run()
print("Districts standardized!")
