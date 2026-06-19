import json, sys
sys.stdout.reconfigure(encoding="utf-8")

# Official totals from PDF image
PDF_TOTALS = {
    "total_intake":    6255,
    "total_kea":       6255,
    "kea_ph":          313,
    "kea_spl":         68,
    "kea_hk":          1394,
    "kea_rk":          4480,
    "kea_tot":         5874,
    "over_above_5pct": 313,
}

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

ann_a = [c for c in d["colleges"] if c["annexure"] == "A"]

# Compute our sums from course-level data
our = {
    "total_intake":    0,
    "total_kea":       0,
    "kea_ph":          0,
    "kea_spl":         0,
    "kea_hk":          0,
    "kea_rk":          0,
    "kea_tot":         0,
    "over_above_5pct": 0,
}

for college in ann_a:
    for c in college["courses"]:
        our["total_intake"]    += c.get("total_intake", 0)
        our["total_kea"]       += c.get("total_kea_seats", 0)
        our["kea_ph"]          += c.get("kea_ph", 0)
        our["kea_spl"]         += c.get("kea_spl", 0)
        our["kea_hk"]          += c.get("kea_hk", 0)
        our["kea_rk"]          += c.get("kea_rk", 0)
        our["kea_tot"]         += c.get("kea_tot", 0)
        our["over_above_5pct"] += c.get("over_above_5pct", 0)

FIELD_LABELS = {
    "total_intake":    "Total Intake",
    "total_kea":       "Total KEA Seats",
    "kea_ph":          "PH 5%",
    "kea_spl":         "SPL",
    "kea_hk":          "HK",
    "kea_rk":          "RK",
    "kea_tot":         "TOT HK-RK Seats",
    "over_above_5pct": "Over & Above SNQ 5%",
}

SEP = "-" * 65
print(SEP)
print("  ANNEXURE A TOTALS: PDF vs Extracted")
print(SEP)
print(f"  {'Field':<22} {'PDF':>8} {'Ours':>8} {'Diff':>8} {'Status'}")
print(SEP)

all_ok = True
for key, label in FIELD_LABELS.items():
    pdf_val = PDF_TOTALS[key]
    our_val = our[key]
    diff    = our_val - pdf_val
    if diff == 0:
        status = "OK"
    else:
        status = f"OFF by {diff:+d}"
        all_ok = False
    marker = "" if diff == 0 else " <---"
    print(f"  {label:<22} {pdf_val:>8} {our_val:>8} {diff:>+8}  {status}{marker}")

print(SEP)
if all_ok:
    print("  RESULT: ALL TOTALS MATCH PERFECTLY")
else:
    print("  RESULT: MISMATCHES FOUND - investigating per-college breakdown")
    print()

    # Find which colleges contribute to mismatches
    print("  Per-college breakdown of mismatching fields:")
    mismatch_fields = [k for k in FIELD_LABELS if PDF_TOTALS[k] != our[k]]

    for college in sorted(ann_a, key=lambda x: x["college_number"]):
        col_sums = {k: 0 for k in mismatch_fields}
        for c in college["courses"]:
            col_sums["kea_ph"]          = col_sums.get("kea_ph", 0)          + c.get("kea_ph", 0)
            col_sums["kea_spl"]         = col_sums.get("kea_spl", 0)         + c.get("kea_spl", 0)
            col_sums["kea_hk"]          = col_sums.get("kea_hk", 0)          + c.get("kea_hk", 0)
            col_sums["kea_rk"]          = col_sums.get("kea_rk", 0)          + c.get("kea_rk", 0)
            col_sums["kea_tot"]         = col_sums.get("kea_tot", 0)         + c.get("kea_tot", 0)
            col_sums["over_above_5pct"] = col_sums.get("over_above_5pct", 0) + c.get("over_above_5pct", 0)
            col_sums["total_intake"]    = col_sums.get("total_intake", 0)    + c.get("total_intake", 0)
            col_sums["total_kea"]       = col_sums.get("total_kea", 0)       + c.get("total_kea_seats", 0)

        name = f"#{college['college_number']:>2} {college['college_name'][:45]}"
        fields_str = "  ".join(
            f"{FIELD_LABELS[f].split()[0]}={col_sums.get(f,0)}"
            for f in mismatch_fields
        )
        print(f"    {name:<50} {fields_str}")

print(SEP)
print(f"  Total Annexure A colleges: {len(ann_a)}/23")
