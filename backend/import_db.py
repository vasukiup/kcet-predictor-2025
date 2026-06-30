import json
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def import_database():
    db_path = os.path.join("backend", "kcet.db")
    schema_path = os.path.join("backend", "schema.sql")
    data_path = "seat_matrix_data.json"
    
    print(f"Connecting to SQLite database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Executing schema from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
        
    print("Clearing existing data...")
    cursor.execute("DELETE FROM cutoffs")
    cursor.execute("DELETE FROM courses")
    cursor.execute("DELETE FROM colleges")
    
    print(f"Loading seat matrix data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    col_count = 0
    course_count = 0
    cutoff_count = 0
    
    try:
        # Wrap in conn context manager for automatic transaction commit/rollback
        with conn:
            for col in data.get("colleges", []):
                cursor.execute("""
                    INSERT INTO colleges (college_number, college_name, address, annexure, college_type, district, total_intake, total_kea_seats)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    col.get("college_number"),
                    col.get("college_name"),
                    col.get("address"),
                    col.get("annexure"),
                    col.get("college_type"),
                    col.get("district"),
                    col.get("total_intake"),
                    col.get("total_kea_seats")
                ))
                college_id = cursor.lastrowid
                col_count += 1
                
                for c in col.get("courses", []):
                    cursor.execute("""
                        INSERT INTO courses (
                            college_id, course_name, total_intake, total_kea_seats, snq_5pct, kea_ph, kea_spl,
                            kea_hk, kea_rk, kea_tot, cat2_seats, cat3_seats, over_above_5pct,
                            sports, ncc, sct_guides, defence, k_defence, ex_defence, capf, ai, xcapf, tot_special_seats
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        college_id,
                        c.get("course_name"),
                        c.get("total_intake", 0),
                        c.get("total_kea_seats", 0),
                        c.get("snq_5pct", 0),
                        c.get("kea_ph", 0),
                        c.get("kea_spl", 0),
                        c.get("kea_hk", 0),
                        c.get("kea_rk", 0),
                        c.get("kea_tot", 0),
                        c.get("cat2_seats", 0),
                        c.get("cat3_seats", 0),
                        c.get("over_above_5pct", 0),
                        c.get("sports", 0),
                        c.get("ncc", 0),
                        c.get("sct_guides", 0),
                        c.get("defence", 0),
                        c.get("k_defence", 0),
                        c.get("ex_defence", 0),
                        c.get("capf", 0),
                        c.get("ai", 0),
                        c.get("xcapf", 0),
                        c.get("tot_special_seats", 0)
                    ))
                    course_id = cursor.lastrowid
                    course_count += 1
                    
                    # Import cutoffs
                    for rd in [1, 2, 3]:
                        cutoff_dict = c.get(f"round{rd}_cutoff") or {}
                        for cat, rank in cutoff_dict.items():
                            if rank is not None:
                                try:
                                    rank_int = int(str(rank).replace(",", "").strip())
                                    cursor.execute("""
                                        INSERT INTO cutoffs (course_id, round, category, cutoff_rank)
                                        VALUES (?, ?, ?, ?)
                                    """, (course_id, rd, cat, rank_int))
                                    cutoff_count += 1
                                except ValueError:
                                    pass
        print("Data imported successfully!")
        print(f"  Colleges: {col_count}")
        print(f"  Courses: {course_count}")
        print(f"  Cut-offs: {cutoff_count}")
    except Exception as e:
        print(f"Error during import: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    import_database()
