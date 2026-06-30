import json

with open("course_standardization_map.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

for k, v in sorted(mapping.items()):
    if v == "Computer Science and Engineering" or "Computer Science and Engineering" in k:
        print(f"'{k}' -> '{v}'")
