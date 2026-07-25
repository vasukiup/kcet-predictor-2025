"""
Create the build_EV.py script to extract all colleges and courses from Annexures E and V,
construct the JSON representation, verify each against the page/college level totals (TOT rows),
and save to seat_matrix_data.json.
We will handle:
- Annexure E (184 colleges, calculated totals: 114,196 intake, 53,052 KEA, 3,900 PH, 1,080 SPL, 7,172 HK, 45,880 RK)
- Annexure V (30 colleges, calculated totals: 32,704 intake, 13,919 KEA, 1,001 PH, 273 SPL, 1,740 HK, 12,179 RK)
Wait, let's also verify that we map the districts properly!
For colleges in E and V, we want to look up their district.
Let's see if we can resolve the district from the college name or address or another source.
Wait! We already have most colleges in the JSON from other annexures (e.g. A, B, C, D have matching college names)!
Let's write a district mapping logic that uses existing college districts if college name matches,
or maps by address city keyword otherwise, and ensures there is no "Other" district.
"""
import pdfplumber, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")

# Let's read the existing seat_matrix_data.json to get known college name -> district mapping
with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

known_districts = {}
for c in d["colleges"]:
    name_clean = re.sub(r'[^A-Z0-9]', '', c["college_name"].upper())
    known_districts[name_clean] = c["district"]

# Let's write the parsing logic for E and V, and save them.
# We will write this in build_EV.py.
