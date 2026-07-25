# =======================================================
# Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
# Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
# Application: KEA Seat Matrix & Prediction Portal
# =======================================================
"""
Database Migration and Seeder Tool.
Loads raw JSON seat matrices/cutoffs and populates the PostgreSQL database.
"""
import os
import json
import re
import sys
import psycopg2

sys.stdout.reconfigure(encoding="utf-8")

def migrate_database():
    # Load connection parameters from environment or default
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "kcet")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "postgres")

    print(f"Connecting to PostgreSQL database: {db_name} on {db_host}:{db_port}...")
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        print("Please ensure your PostgreSQL container/service is running and accessible.")
        sys.exit(1)

    cursor = conn.cursor()

    print("Dropping existing tables to refresh schema...")
    cursor.execute("DROP TABLE IF EXISTS cutoffs, courses, colleges CASCADE;")
    conn.commit()

    # Load and execute the schema script
    schema_path = os.path.join("backend", "schema_postgres.sql")
    print(f"Executing schema from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.execute(f.read())
    conn.commit()

    datasets = [
        (2026, "seat_matrix_data_2026.json"),
        (2025, "seat_matrix_data.json"),
        (2024, "seat_matrix_data_2024.json")
    ]

    total_cols = 0
    total_courses = 0
    total_cutoffs = 0

    try:
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
                # Retrieve enriched metadata
                established = col.get("established") or col.get("established_year")
                nirf = col.get("nirf_rank")
                naac = col.get("naac_grade")
                nba = col.get("nba_accredited")
                
                placements = col.get("placements") or {}
                avg_pkg = placements.get("avg_package") or placements.get("average_package")
                max_pkg = placements.get("highest_package") or placements.get("max_package")
                pct_placed = placements.get("placement_rate")

                hostels = col.get("hostel_details") or {}
                h_fees = hostels.get("hostel_fees")
                h_cap = hostels.get("hostel_capacity")
                h_mess = hostels.get("mess_included")

                campus = col.get("campus_life") or {}
                c_size = campus.get("campus_size")
                c_dist = campus.get("majestic_dist_km") or campus.get("distance_to_majestic")
                c_transit = campus.get("nearest_transit")

                # Insert into colleges
                cursor.execute("""
                    INSERT INTO colleges (
                        college_number, kea_code, college_name, address, annexure, college_type, district, total_intake, total_kea_seats, year,
                        established_year, nirf_rank, naac_grade, nba_accredited, placements_avg_package, placements_highest_package, placements_rate,
                        hostel_fees, hostel_capacity, hostel_mess_included, campus_size, campus_majestic_dist_km, campus_nearest_transit
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (
                    col.get("college_number"),
                    col.get("kea_code"),
                    col.get("college_name"),
                    col.get("address"),
                    col.get("annexure"),
                    col.get("college_type"),
                    col.get("district"),
                    col.get("total_intake"),
                    col.get("total_kea_seats"),
                    year,
                    int(established) if established else None,
                    int(nirf) if nirf else None,
                    naac,
                    nba,
                    str(avg_pkg) if avg_pkg else None,
                    str(max_pkg) if max_pkg else None,
                    str(pct_placed) if pct_placed else None,
                    str(h_fees) if h_fees else None,
                    str(h_cap) if h_cap else None,
                    str(h_mess) if h_mess else None,
                    c_size,
                    float(c_dist) if c_dist else None,
                    c_transit
                ))
                college_id = cursor.fetchone()[0]
                col_count += 1

                for cr in col.get("courses", []):
                    c_placements = cr.get("course_placements") or {}
                    c_min = c_placements.get("min_package")
                    c_avg = c_placements.get("avg_package") or c_placements.get("average_package")
                    c_max = c_placements.get("max_package") or c_placements.get("highest_package")
                    c_pct = c_placements.get("placement_rate")
                    c_industry = c_placements.get("industry")
                    
                    recruiters_val = c_placements.get("recruiters")
                    if isinstance(recruiters_val, list):
                        c_recruiters = ", ".join(recruiters_val)
                    else:
                        c_recruiters = recruiters_val

                    # Insert into courses
                    cursor.execute("""
                        INSERT INTO courses (
                            college_id, course_name, total_intake, total_kea_seats, snq_5pct, kea_ph, kea_spl,
                            kea_hk, kea_rk, kea_tot, cat2_seats, cat3_seats, over_above_5pct,
                            sports, ncc, sct_guides, defence, k_defence, ex_defence, capf, ai, xcapf, tot_special_seats, year,
                            placements_min_package, placements_avg_package, placements_max_package, placements_rate, placements_industry, placements_recruiters
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (
                        college_id,
                        cr.get("course_name"),
                        cr.get("total_intake", 0),
                        cr.get("total_kea_seats", 0),
                        cr.get("snq_5pct", 0),
                        cr.get("kea_ph", 0),
                        cr.get("kea_spl", 0),
                        cr.get("kea_hk", 0),
                        cr.get("kea_rk", 0),
                        cr.get("kea_tot", 0),
                        cr.get("cat2_seats", 0),
                        cr.get("cat3_seats", 0),
                        cr.get("over_above_5pct", 0),
                        cr.get("sports", 0),
                        cr.get("ncc", 0),
                        cr.get("sct_guides", 0),
                        cr.get("defence", 0),
                        cr.get("k_defence", 0),
                        cr.get("ex_defence", 0),
                        cr.get("capf", 0),
                        cr.get("ai", 0),
                        cr.get("xcapf", 0),
                        cr.get("tot_special_seats", 0),
                        year,
                        str(c_min) if c_min else None,
                        str(c_avg) if c_avg else None,
                        str(c_max) if c_max else None,
                        str(c_pct) if c_pct else None,
                        c_industry,
                        c_recruiters
                    ))
                    course_id = cursor.fetchone()[0]
                    course_count += 1

                    rounds_to_import = [
                        (1, "round1_cutoff"),
                        (2, "round2_cutoff"),
                        (3, "round3_cutoff"),
                        (0, "mock_round1_cutoff")
                    ]
                    for rd, key in rounds_to_import:
                        cutoff_dict = cr.get(key) or {}
                        for cat, rank in cutoff_dict.items():
                            if rank is not None:
                                try:
                                    rank_clean = re.sub(r'[^\d]', '', str(rank))
                                    if rank_clean:
                                        rank_int = int(rank_clean)
                                        cursor.execute("""
                                            INSERT INTO cutoffs (course_id, round, category, cutoff_rank, year)
                                            VALUES (%s, %s, %s, %s, %s)
                                        """, (course_id, rd, cat, rank_int, year))
                                        cutoff_count += 1
                                except ValueError:
                                    pass

            print(f"Year {year} data imported:")
            print(f"  Colleges: {col_count}")
            print(f"  Courses: {course_count}")
            print(f"  Cut-offs: {cutoff_count}")
            total_cols += col_count
            total_courses += course_count
            total_cutoffs += cutoff_count

        conn.commit()
        print("\nAll data migrated successfully to PostgreSQL!")
        print(f"  Total Colleges: {total_cols}")
        print(f"  Total Courses: {total_courses}")
        print(f"  Total Cut-offs: {total_cutoffs}")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
