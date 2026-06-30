import json
import re

def clean_name(name):
    n = name.lower()
    n = n.replace('&', 'and')
    n = n.replace('engg', 'engineering')
    n = n.replace('tech', 'technology')
    n = n.replace('coll', 'college')
    n = n.replace('inst', 'institute')
    n = n.replace('univ', 'university')
    n = n.replace('sch', 'school')
    n = n.replace('dept', 'department')
    n = re.sub(r'[^a-z0-9]', '', n)
    return n

with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

std_cols = [c for c in db["colleges"] if c["annexure"] not in ("E", "V")]

# Look for KLE Belgaum in std_cols
kle_list = [c for c in std_cols if "sheshagiri" in c["college_name"].lower()]
print(f"KLE Belgaum count in std_cols: {len(kle_list)}")
for col in kle_list:
    print(f"  Name: '{col['college_name']}'")
    print(f"  Clean: '{clean_name(col['college_name'])}'")
    
# Look for Sapthagiri in std_cols
sapth_list = [c for c in std_cols if "sapthagiri" in c["college_name"].lower()]
print(f"\nSapthagiri count in std_cols: {len(sapth_list)}")
for col in sapth_list:
    print(f"  Name: '{col['college_name']}'")
    print(f"  Clean: '{clean_name(col['college_name'])}'")
