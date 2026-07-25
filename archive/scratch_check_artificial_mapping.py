import json

with open("course_standardization_map.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

for k, v in mapping.items():
    if "ARTIFICIAL" in k:
        print(f"'{k}' -> '{v}'")
