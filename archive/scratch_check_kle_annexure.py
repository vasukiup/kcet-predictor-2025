import json

with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for idx, col in enumerate(db["colleges"]):
    name = col["college_name"]
    ann = col.get("annexure")
    if "sheshagiri" in name.lower():
        print(f"Index: {idx}, Annexure: {ann}, Name: '{name}'")
