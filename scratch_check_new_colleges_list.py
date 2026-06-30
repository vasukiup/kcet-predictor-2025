from extract_seats_v2 import extract_all, build_output
colleges = extract_all()
new_output = build_output(colleges)

ann_counts = {}
for col in new_output["colleges"]:
    ann = col["annexure"]
    ann_counts[ann] = ann_counts.get(ann, 0) + 1
print("New counts by annexure:", ann_counts)

# Let's print colleges in Annexure D to see if there are duplicates
print("\nAnnexure D colleges:")
for col in new_output["colleges"]:
    if col["annexure"] == "D":
        print(f"  - #{col['college_number']}: {col['college_name']}")
