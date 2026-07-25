from extract_seats_v2 import extract_all

colleges = extract_all()
for col in colleges:
    # Print if annexure is not A, B, C, D or if there's something weird
    print(f"[{col['annexure']}] #{col['college_number']} {col['college_name']}")
