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

# Find Balekundri in database
db_name = next(c["college_name"] for c in db["colleges"] if "balekundri" in c["college_name"].lower())
pdf_name = "S.S.E.T.S.S.G.Balekundri Institute of Technology, Shivabasavanagar, Belgaum"

print(f"DB Name:  '{db_name}'")
print(f"PDF Name: '{pdf_name}'")
print(f"DB Cleaned:  '{clean_name(db_name)}'")
print(f"PDF Cleaned: '{clean_name(pdf_name)}'")
print(f"Match? {clean_name(db_name) == clean_name(pdf_name)}")
