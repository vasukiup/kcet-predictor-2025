-- Schema for KCET Predictor Database

CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_number INTEGER NOT NULL,
    college_name TEXT NOT NULL,
    address TEXT,
    annexure TEXT NOT NULL,
    college_type TEXT,
    district TEXT,
    total_intake INTEGER,
    total_kea_seats INTEGER
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
    FOREIGN KEY(college_id) REFERENCES colleges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cutoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    category TEXT NOT NULL,
    cutoff_rank INTEGER NOT NULL,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_colleges_annexure ON colleges(annexure);
CREATE INDEX IF NOT EXISTS idx_courses_college ON courses(college_id);
CREATE INDEX IF NOT EXISTS idx_cutoffs_course ON cutoffs(course_id);
CREATE INDEX IF NOT EXISTS idx_cutoffs_lookup ON cutoffs(category, cutoff_rank);
