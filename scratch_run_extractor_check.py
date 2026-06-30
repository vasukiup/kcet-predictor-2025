from extract_seats_v2 import extract_all
import json

colleges = extract_all()
for col in colleges:
    if col["college_number"] in [134, 136]:
        print(col["college_name"])
        for c in col["courses"]:
            print(f"  - {c['course_name']} (Intake: {c['total_intake']})")
