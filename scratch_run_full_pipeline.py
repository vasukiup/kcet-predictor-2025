import subprocess
import sys
import shutil

def run_script(name):
    print(f"\n=================== RUNNING {name} ===================")
    res = subprocess.run([sys.executable, name], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(f"Error in {name}:", res.stderr)
    if res.returncode != 0:
        print(f"FAILED: {name} returned non-zero code {res.returncode}")
        sys.exit(1)

# Step 1: Copy baseline to seat_matrix_data.json
shutil.copyfile("seat_matrix_data_v1_baseline.json", "seat_matrix_data.json")
print("Restored seat_matrix_data.json from seat_matrix_data_v1_baseline.json")

# Step 1.5: Fix column mapping shifts in Annexures A & C in the baseline copy
run_script("fix_baseline_shifted_columns.py")
run_script("fix_annC_and_add_yenepoya.py")

# Step 2: Run all builders in order
run_script("rebuild_annB.py")
run_script("add_annB_78.py")
run_script("rebuild_annD_M.py")
run_script("add_annZ_12.py")
run_script("add_annP_12.py")
run_script("final_annO.py")
run_script("parse_special_category.py")
run_script("standardize_course_names.py")
run_script("standardize_districts.py")
run_script("merge_zero_intake_duplicates.py")
run_script("fix_districts.py")
run_script("standardize_districts.py")
run_script("run_final_mapping.py")

# Step 3: Rename colleges with duplicate names to distinguish them by appending their KEA code
print("\n=================== DISTINGUISHING DUPLICATE NAMES ===================")
import json
with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
    db = json.load(f)

name_groups = {}
for col in db["colleges"]:
    name = col["college_name"]
    name_groups.setdefault(name, []).append(col)

for name, cols in name_groups.items():
    if len(cols) > 1:
        for col in cols:
            code = col.get("kea_code")
            if code:
                col["college_name"] = f"{name} ({code})"
                print(f"  Renamed duplicate college: '{name}' -> '{col['college_name']}'")

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

run_script("regen_stats.py")

print("\nALL SCRIPTS IN THE PIPELINE EXECUTED SUCCESSFULLY!")
