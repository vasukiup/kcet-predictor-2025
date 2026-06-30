import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

def fix_baseline_shifted_columns():
    print("Loading seat_matrix_data.json...")
    with open("seat_matrix_data.json", encoding="utf-8") as f:
        db = json.load(f)

    fixed_a = 0
    fixed_c = 0

    for col in db["colleges"]:
        ann = col["annexure"]
        
        # 1. Correct Government / VTU Colleges (Annexure A)
        if ann == "A":
            # Skip college 23, which is manually entered and correct
            if col["college_number"] == 23:
                continue
                
            for c in col["courses"]:
                old_snq  = c.get("snq_5pct", 0) or 0
                old_ph   = c.get("kea_ph", 0) or 0
                old_spl  = c.get("kea_spl", 0) or 0
                old_hk   = c.get("kea_hk", 0) or 0
                old_rk   = c.get("kea_rk", 0) or 0
                old_tot  = c.get("kea_tot", 0) or 0
                old_over = c.get("over_above_5pct", 0) or 0

                c["kea_ph"]          = old_snq
                c["kea_spl"]         = old_ph
                c["kea_hk"]          = old_spl
                c["kea_rk"]          = old_hk
                c["kea_tot"]         = old_rk
                c["over_above_5pct"] = old_tot
                c["snq_5pct"]        = old_tot
                
                # Enforce exclusive sum for KEA seats
                c["total_kea_seats"] = c["kea_ph"] + c["kea_spl"] + c["kea_hk"] + c["kea_rk"]
                fixed_a += 1
                
            col["total_intake"] = sum(c["total_intake"] for c in col["courses"])
            col["total_kea_seats"] = sum(c["total_kea_seats"] for c in col["courses"])

        # 2. Correct Private Unaided Colleges (Annexure C)
        elif ann == "C":
            # Skip college 147 (Yenepoya) as it is added with correct columns later in the pipeline
            if col["college_number"] == 147:
                continue
                
            for c in col["courses"]:
                old_snq  = c.get("snq_5pct", 0) or 0
                old_ph   = c.get("kea_ph", 0) or 0
                old_spl  = c.get("kea_spl", 0) or 0
                old_hk   = c.get("kea_hk", 0) or 0
                old_rk   = c.get("kea_rk", 0) or 0
                old_tot  = c.get("kea_tot", 0) or 0
                old_cat2 = c.get("cat2_seats", 0) or 0
                old_cat3 = c.get("cat3_seats", 0) or 0
                old_over = c.get("over_above_5pct", 0) or 0

                c["kea_ph"]          = old_snq
                c["kea_spl"]         = old_ph
                c["kea_hk"]          = old_spl
                c["kea_rk"]          = old_hk
                c["kea_tot"]         = old_rk
                c["cat2_seats"]      = old_tot
                c["cat3_seats"]      = old_cat2
                c["over_above_5pct"] = old_cat3
                c["snq_5pct"]        = old_over
                
                # Enforce exclusive sum for KEA seats
                c["total_kea_seats"] = c["kea_ph"] + c["kea_spl"] + c["kea_hk"] + c["kea_rk"]
                fixed_c += 1
                
            col["total_intake"] = sum(c["total_intake"] for c in col["courses"])
            col["total_kea_seats"] = sum(c["total_kea_seats"] for c in col["courses"])

    print(f"Shift correction applied to {fixed_a} course rows in Annexure A.")
    print(f"Shift correction applied to {fixed_c} course rows in Annexure C.")

    with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("Saved corrected seat_matrix_data.json.")

if __name__ == "__main__":
    fix_baseline_shifted_columns()
