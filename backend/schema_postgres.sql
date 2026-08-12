-- =======================================================
-- Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
-- Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
-- Application: KEA Seat Matrix & Prediction Portal
-- =======================================================
-- Schema for KCET Predictor PostgreSQL Database

CREATE TABLE IF NOT EXISTS colleges (
    id SERIAL PRIMARY KEY,
    college_number INTEGER NOT NULL,
    kea_code TEXT,
    college_name TEXT NOT NULL,
    address TEXT,
    annexure TEXT NOT NULL,
    college_type TEXT,
    district TEXT,
    total_intake INTEGER,
    total_kea_seats INTEGER,
    year INTEGER DEFAULT 2025,
    
    -- Enriched Metadata Columns
    established_year INTEGER,
    nirf_rank INTEGER,
    naac_grade TEXT,
    nba_accredited TEXT,
    placements_avg_package TEXT,
    placements_highest_package TEXT,
    placements_rate TEXT,
    hostel_fees TEXT,
    hostel_capacity TEXT,
    hostel_mess_included TEXT,
    campus_size TEXT,
    campus_majestic_dist_km REAL,
    campus_nearest_transit TEXT
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    college_id INTEGER NOT NULL,
    course_name TEXT NOT NULL,
    total_intake INTEGER DEFAULT 0,
    total_kea_seats INTEGER DEFAULT 0,
    snq_5pct INTEGER DEFAULT 0,
    kea_ph INTEGER DEFAULT 0,
    kea_spl INTEGER DEFAULT 0,
    kea_hk INTEGER DEFAULT 0,
    kea_rk INTEGER DEFAULT 0,
    kea_tot INTEGER DEFAULT 0,
    cat2_seats INTEGER DEFAULT 0,
    cat3_seats INTEGER DEFAULT 0,
    over_above_5pct INTEGER DEFAULT 0,
    sports INTEGER DEFAULT 0,
    ncc INTEGER DEFAULT 0,
    sct_guides INTEGER DEFAULT 0,
    defence INTEGER DEFAULT 0,
    k_defence INTEGER DEFAULT 0,
    ex_defence INTEGER DEFAULT 0,
    capf INTEGER DEFAULT 0,
    ai INTEGER DEFAULT 0,
    xcapf INTEGER DEFAULT 0,
    tot_special_seats INTEGER DEFAULT 0,
    year INTEGER DEFAULT 2025,
    
    -- Course Placements Columns
    placements_min_package TEXT,
    placements_avg_package TEXT,
    placements_max_package TEXT,
    placements_rate TEXT,
    placements_industry TEXT,
    placements_recruiters TEXT,

    FOREIGN KEY(college_id) REFERENCES colleges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cutoffs (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    category TEXT NOT NULL,
    cutoff_rank BIGINT NOT NULL,
    year INTEGER DEFAULT 2025,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Performance Indexes for High Concurrency Queries
CREATE INDEX IF NOT EXISTS idx_pg_colleges_annexure ON colleges(annexure);
CREATE INDEX IF NOT EXISTS idx_pg_colleges_year ON colleges(year);
CREATE INDEX IF NOT EXISTS idx_pg_courses_college ON courses(college_id);
CREATE INDEX IF NOT EXISTS idx_pg_courses_year ON courses(year);
CREATE INDEX IF NOT EXISTS idx_pg_cutoffs_course ON cutoffs(course_id);
CREATE INDEX IF NOT EXISTS idx_pg_cutoffs_year ON cutoffs(year);
CREATE INDEX IF NOT EXISTS idx_pg_cutoffs_lookup ON cutoffs(category, cutoff_rank);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- holds salt:hash
    role TEXT NOT NULL, -- 'student', 'counsellor', 'institution', 'authority', 'superuser'
    rank INTEGER,
    category TEXT,
    region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    username TEXT,
    action TEXT NOT NULL, -- 'REGISTER', 'LOGIN', 'PREDICTION', 'OPTION_OPTIMIZE', 'DOWNLOAD', 'COMPARE'
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pg_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_pg_audit_logs_timestamp ON audit_logs(timestamp);
