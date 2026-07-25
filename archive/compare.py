import json, sys
sys.stdout.reconfigure(encoding="utf-8")

PDF_GROUND_TRUTH = {
    "A": {"label": "Government / VTU",  "colleges": 22},
    "B": {"label": "Government Aided",  "colleges": 8},
    "C": {"label": "Private Unaided",   "colleges": 146},
    "D": {"label": "Private Minority",  "colleges": 25},
}

with open("seat_matrix_data_v1_baseline.json", encoding="utf-8") as f:
    v1 = json.load(f)
with open("seat_matrix_data.json", encoding="utf-8") as f:
    v2 = json.load(f)

def ann_stats(data, ann):
    cols = [c for c in data["colleges"] if c["annexure"] == ann]
    seats = sum(c.get("total_intake", 0) for c in cols)
    kea   = sum(c.get("total_kea_seats", 0) for c in cols)
    zero  = sum(1 for c in cols if not c.get("courses"))
    mismatches = sum(
        1 for c in cols
        if c.get("total_intake", 0) > 0
        and abs(c.get("total_intake", 0) - sum(x.get("total_intake", 0) for x in c.get("courses", []))) > 5
    )
    return len(cols), seats, kea, zero, mismatches

SEP = "-" * 72
print(SEP)
print("BEFORE vs AFTER vs PDF GROUND TRUTH")
print(SEP)

total_v1 = total_v2 = total_pdf = 0

for ann in ["A", "B", "C", "D"]:
    gt = PDF_GROUND_TRUTH[ann]
    c1, s1, k1, z1, m1 = ann_stats(v1, ann)
    c2, s2, k2, z2, m2 = ann_stats(v2, ann)
    g = gt["colleges"]
    ok1 = "EXACT" if c1 == g else f"{c1 - g:+d}"
    ok2 = "EXACT" if c2 == g else f"{c2 - g:+d}"

    label = f"Annexure {ann} - {gt['label']}"
    print(label)
    print(f"  {'':26} {'v1':>8} {'v2':>8} {'PDF':>8}")
    print(f"  {'Colleges':26} {c1:>8} {c2:>8} {g:>8}    v1={ok1}  v2={ok2}")
    print(f"  {'Total Seats':26} {s1:>8,} {s2:>8,}")
    print(f"  {'KEA Seats':26} {k1:>8,} {k2:>8,}")
    print(f"  {'Colleges w/0 courses':26} {z1:>8} {z2:>8}")
    print(f"  {'Intake mismatches':26} {m1:>8} {m2:>8}")
    total_v1 += c1
    total_v2 += c2
    total_pdf += g
    print()

print(SEP)
print("TOTALS")
print(SEP)

all1 = v1["colleges"]
all2 = v2["colleges"]
ts1 = sum(c.get("total_intake", 0) for c in all1)
ts2 = sum(c.get("total_intake", 0) for c in all2)
tk1 = sum(c.get("total_kea_seats", 0) for c in all1)
tk2 = sum(c.get("total_kea_seats", 0) for c in all2)
cr1 = v1["metadata"]["total_courses_offered"]
cr2 = v2["metadata"]["total_courses_offered"]

print(f"  {'':26} {'v1':>8} {'v2':>8} {'PDF':>8}")
print(f"  {'Total Colleges':26} {total_v1:>8} {total_v2:>8} {total_pdf:>8}    v1={total_v1 - total_pdf:+d}  v2={total_v2 - total_pdf:+d}")
print(f"  {'Total Seats':26} {ts1:>8,} {ts2:>8,}")
print(f"  {'Total KEA Seats':26} {tk1:>8,} {tk2:>8,}")
print(f"  {'Unique Courses':26} {cr1:>8} {cr2:>8}")
