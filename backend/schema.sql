-- Schema for KCET Predictor Database

CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_number INTEGER NOT NULL,
    kea_code TEXT,
    college_name TEXT NOT NULL,
    address TEXT,
    annexure TEXT NOT NULL,
    college_type TEXT,
    district TEXT,
    total_intake INTEGER,
    total_kea_seats INTEGER,
    year INTEGER DEFAULT 2025
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    FOREIGN KEY(college_id) REFERENCES colleges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cutoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    category TEXT NOT NULL,
    cutoff_rank INTEGER NOT NULL,
    year INTEGER DEFAULT 2025,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_colleges_annexure ON colleges(annexure);
CREATE INDEX IF NOT EXISTS idx_colleges_year ON colleges(year);
CREATE INDEX IF NOT EXISTS idx_courses_college ON courses(college_id);
CREATE INDEX IF NOT EXISTS idx_courses_year ON courses(year);
CREATE INDEX IF NOT EXISTS idx_cutoffs_course ON cutoffs(course_id);
CREATE INDEX IF NOT EXISTS idx_cutoffs_year ON cutoffs(year);
CREATE INDEX IF NOT EXISTS idx_cutoffs_lookup ON cutoffs(category, cutoff_rank);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- holds salt:hash
    role TEXT NOT NULL DEFAULT 'student', -- 'student', 'counsellor', 'institution', 'authority', 'superuser'
    rank INTEGER,
    category TEXT,
    region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
