import json, sys
sys.stdout.reconfigure(encoding="utf-8")

# PDF says Total A intake = 6255
# We have 6195 = 6255 - 60 missing
# All differences: intake -60, ph -3, spl -1, hk -4, rk -52, tot -56, over -3
# 
# The only college we know has a mismatch is #21 (VIAT Muddenahalli)
# which was noted to be missing 60 seats (claimed=450, extracted=390)
# 390 + 60 = 450... wait, let me re-read
# From old report: VISVESVARAYA TECHNOLOGICAL UNIVERSITY, BELAGAVI, VIAT: claimed=450, extracted=390, missing=60
# So the college TOTAL shows 450 but our sum of courses = 390 (1 course missing)
# 
# But after the column fix, our total_intake field hasn't changed (it's still from nums[0] and nums[1])
# total_intake and total_kea_seats on courses come from nums[0] and nums[1] - they were correct
# So the 60 missing = one missing course row for college #21

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

# Check college #21
col21 = next(c for c in d["colleges"] if c["annexure"] == "A" and c["college_number"] == 21)
print("College #21:", col21["college_name"])
print(f"  Stored total_intake: {col21['total_intake']}")
print(f"  Sum of courses:      {sum(c['total_intake'] for c in col21['courses'])}")
print(f"  Courses ({len(col21['courses'])}):")
for c in col21["courses"]:
    print(f"    {c['course_name'][:45]:<47} intake={c['total_intake']:>4} kea={c['total_kea_seats']:>4}"
          f" ph={c['kea_ph']:>2} spl={c['kea_spl']:>2} hk={c['kea_hk']:>3} rk={c['kea_rk']:>3}"
          f" tot={c['kea_tot']:>3} over={c['over_above_5pct']:>2}")
print()

# Show all colleges where sum_of_courses != college total
print("Colleges where course sum != stored total (intake):")
ann_a = sorted([c for c in d["colleges"] if c["annexure"] == "A"], key=lambda x: x["college_number"])
total_diff = 0
for college in ann_a:
    s = sum(c["total_intake"] for c in college["courses"])
    t = college["total_intake"]
    if s != t:
        diff = t - s
        total_diff += diff
        print(f"  #{college['college_number']:>2} {college['college_name'][:50]} stored={t} sum={s} missing={diff}")

print(f"\n  Total missing intake across all discrepancies: {total_diff}")
print(f"  We need {6255 - sum(c['total_intake'] for col in ann_a for c in col['courses'])} more seats to match PDF")
