import json
from build_EV import parse_annexure_data

# Parse Annexure V using the same logic as build_EV.py
try:
    ann_v_colleges = parse_annexure_data("Seat_Matrix_05072025.pdf", range(325, 361), "V")
    print(f"Total colleges parsed in V: {len(ann_v_colleges)}")
    
    # Look for Amity
    amity_v = [c for c in ann_v_colleges if "AMITY" in c["college_name"].upper()]
    if amity_v:
        for idx, col in enumerate(amity_v):
            print(f"\nFound Amity in parsed Annexure V (index {idx}):")
            print(f"College Name: '{col['college_name']}', Number: {col['college_number']}")
            print(f"Type: '{col['college_type']}', District: '{col['district']}'")
            print(f"Total Intake: {col['total_intake']}, Total KEA Seats: {col['total_kea_seats']}")
            print("Courses:")
            for cr in col["courses"]:
                print(f"  - '{cr['course_name']}': intake={cr['total_intake']}, KEA={cr['total_kea_seats']}")
    else:
        print("\nAMITY UNIVERSITY not found in parsed Annexure V!")
except Exception as e:
    import traceback
    traceback.print_exc()
