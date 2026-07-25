import json

# Let's run extract_seats.py
from extract_seats import extract_all, build_output
colleges = extract_all()
out = build_output(colleges)

print("v1 extractor stats:")
print(f"  Colleges: {len(out['colleges'])}")
print(f"  Seats: {sum(c.get('total_intake', 0) for c in out['colleges'])}")
print(f"  KEA: {sum(c.get('total_kea_seats', 0) for c in out['colleges'])}")
