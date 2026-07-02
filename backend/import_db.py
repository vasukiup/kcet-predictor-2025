import json
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def import_database():
    db_path = os.path.join("backend", "kcet.db")
    if os.path.exists(db_path):
        print(f"Deleting old database file at {db_path}...")
        try:
            os.remove(db_path)
        except Exception as e:
            print(f"Warning: could not delete old database file: {e}")
            
    schema_path = os.path.join("backend", "schema.sql")
    
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
    
    datasets = [
        (2025, "seat_matrix_data.json"),
        (2024, "seat_matrix_data_2024.json")
    ]
    
    col_count_tot = 0
    course_count_tot = 0
    cutoff_count_tot = 0
    
    try:
        with conn:
            for year, data_path in datasets:
                if not os.path.exists(data_path):
                    print(f"Data file '{data_path}' for year {year} not found. Skipping.")
                    continue
                    
                print(f"Loading seat matrix data from {data_path} for year {year}...")
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                col_count = 0
                course_count = 0
                cutoff_count = 0
                
                for col in data.get("colleges", []):
                    cursor.execute("""
                        INSERT INTO colleges (college_number, college_name, address, annexure, college_type, district, total_intake, total_kea_seats, year)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        col.get("college_number"),
                        col.get("college_name"),
                        col.get("address"),
                        col.get("annexure"),
                        col.get("college_type"),
                        col.get("district"),
                        col.get("total_intake"),
                        col.get("total_kea_seats"),
                        year
                    ))
                    college_id = cursor.lastrowid
                    col_count += 1
                    
                    for c in col.get("courses", []):
                        cursor.execute("""
                            INSERT INTO courses (
                                college_id, course_name, total_intake, total_kea_seats, snq_5pct, kea_ph, kea_spl,
                                kea_hk, kea_rk, kea_tot, cat2_seats, cat3_seats, over_above_5pct,
                                sports, ncc, sct_guides, defence, k_defence, ex_defence, capf, ai, xcapf, tot_special_seats, year
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                            c.get("tot_special_seats", 0),
                            year
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
                                            INSERT INTO cutoffs (course_id, round, category, cutoff_rank, year)
                                            VALUES (?, ?, ?, ?, ?)
                                        """, (course_id, rd, cat, rank_int, year))
                                        cutoff_count += 1
                                    except ValueError:
                                        pass
                print(f"Year {year} data imported:")
                print(f"  Colleges: {col_count}")
                print(f"  Courses: {course_count}")
                print(f"  Cut-offs: {cutoff_count}")
                col_count_tot += col_count
                course_count_tot += course_count
                cutoff_count_tot += cutoff_count
                
        print("\nAll data imported successfully!")
        print(f"  Total Colleges: {col_count_tot}")
        print(f"  Total Courses: {course_count_tot}")
        print(f"  Total Cut-offs: {cutoff_count_tot}")
    except Exception as e:
        print(f"Error during import: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    import_database()
