import json
import os
import sys

# Ensure e:/Antigravity is in path
sys.path.append("e:/Antigravity")
from standardize_course_names import standardize_single_name

def generate_mapping():
    print("Collecting course names from seat_matrix_data.json...")
    with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
        sm_data = json.load(f)
        
    raw_courses = set()
    for col in sm_data["colleges"]:
        for c in col["courses"]:
            raw_courses.add(c["course_name"])
            
    print(f"Collected {len(raw_courses)} course names from seat matrix.")
    
    # Read cutoff files
    cutoff_files = ["round1_cutoffs.json", "round2_cutoffs.json", "round3_cutoffs.json"]
    for filename in cutoff_files:
        if os.path.exists(filename):
            print(f"Collecting course names from {filename}...")
            with open(filename, "r", encoding="utf-8") as f:
                cutoffs = json.load(f)
            for code, info in cutoffs.items():
                for c in info["courses"].keys():
                    raw_courses.add(c)
        else:
            print(f"Warning: {filename} not found.")
            
    print(f"Total unique raw course names collected: {len(raw_courses)}")
    
    # Create the mapping raw_name -> standardized_name
    mapping = {}
    standardized_set = set()
    
    for raw in sorted(list(raw_courses)):
        standardized = standardize_single_name(raw)
        mapping[raw] = standardized
        standardized_set.add(standardized)
        
    print(f"Generated {len(mapping)} mappings pointing to {len(standardized_set)} unique standardized names.")
    
    # Save the mapping
    with open("course_standardization_map.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
        
    print("Successfully saved course_standardization_map.json!")

if __name__ == "__main__":
    generate_mapping()
