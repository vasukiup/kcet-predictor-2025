"""
Regenerate seat_matrix_data.json stats (by_annexure, by_district, by_course)
to reflect updated Annexure D and new Annexure M data.
"""
import json, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

colleges = d["colleges"]

# ── by_annexure ──────────────────────────────────────────────────────────────
ANN_LABELS = {
    "A": "Government / VTU",
    "B": "Govt Aided",
    "C": "Private Unaided",
    "D": "Private Minority",
    "M": "Public University",
    "O": "Private University",
    "P": "Deemed University",
    "Z": "Government (Higher Fees)",
    "E": "New Intake (Govt/Pvt)",
    "V": "New Intake (Univ)",
}
by_ann = {}
for ann, label in ANN_LABELS.items():
    cols = [c for c in colleges if c["annexure"] == ann]
    total = sum(cr["total_intake"] for c in cols for cr in c["courses"])
    kea   = sum(cr["total_kea_seats"] for c in cols for cr in c["courses"])
    cat2  = sum(cr.get("cat2_seats", 0) for c in cols for cr in c["courses"])
    cat3  = sum(cr.get("cat3_seats", 0) for c in cols for cr in c["courses"])
    by_ann[ann] = {
        "label": label,
        "college_count": len(cols),
        "total_seats": total,
        "kea_seats": kea,
        "cat2_seats": cat2,
        "cat3_seats": cat3,
    }
    print(f"  Annexure {ann}: {len(cols)} colleges, {total:,} seats")

# ── by_district ───────────────────────────────────────────────────────────────
dist_map = defaultdict(lambda: {"total": 0, "kea": 0, "colleges": set()})
for c in colleges:
    dist = c.get("district") or "Other"
    dist_map[dist]["colleges"].add(c["college_name"])
    for cr in c["courses"]:
        dist_map[dist]["total"] += cr.get("total_intake", 0)
        dist_map[dist]["kea"]   += cr.get("total_kea_seats", 0)

by_dist = {}
for dist, v in dist_map.items():
    by_dist[dist] = {"total": v["total"], "kea": v["kea"], "college_count": len(v["colleges"])}

# ── by_course ─────────────────────────────────────────────────────────────────
course_map = defaultdict(lambda: {"total": 0, "kea": 0, "count": 0})
for c in colleges:
    for cr in c["courses"]:
        name = cr["course_name"].strip().upper()
        course_map[name]["total"] += cr.get("total_intake", 0)
        course_map[name]["kea"]   += cr.get("total_kea_seats", 0)
        course_map[name]["count"] += 1

by_course = dict(course_map)

# ── summary ───────────────────────────────────────────────────────────────────
total_all = sum(v["total_seats"] for v in by_ann.values())
total_kea = sum(v["kea_seats"] for v in by_ann.values())
total_col = sum(v["college_count"] for v in by_ann.values())

d["stats"] = {
    "total_colleges": total_col,
    "total_seats": total_all,
    "total_kea_seats": total_kea,
    "by_annexure": by_ann,
    "by_district": by_dist,
    "by_course": by_course,
}

# Rebuild all_courses list with standardized course names
all_courses_set = set()
for c in colleges:
    for cr in c["courses"]:
        all_courses_set.add(cr["course_name"].strip())
d["all_courses"] = sorted(list(all_courses_set))

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"\nStats updated:")
print(f"  Total colleges: {total_col}")
print(f"  Total seats:    {total_all:,}")
print(f"  Total KEA:      {total_kea:,}")
print(f"\nBy Annexure:")
for ann, v in by_ann.items():
    print(f"  [{ann}] {v['label']:<28} {v['college_count']:>4} colleges  {v['total_seats']:>8,} seats  {v['kea_seats']:>8,} KEA")
