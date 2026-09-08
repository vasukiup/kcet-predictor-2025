# System Design & Coding Guidelines
**Comprehensive Engineering Best Practices & Post-Mortem Analysis for Educational & Counseling Predictor Applications**

---

## 📌 Executive Summary

This document synthesizes key architectural principles, data engineering standards, post-mortem mistake audits, and backend/frontend reliability protocols established while building the **KEA Seat Matrix & Cutoff Prediction Portal**. 

It serves as a reusable, production-grade blueprint for building similar data-heavy portal applications (such as NEET, JoSAA/CSAB, COMEDK, or state-level counseling predictors).

---

## 📜 Part I: Mistakes Committed, Root Causes & Applied Corrections

Below is a detailed log of real-world bugs, failure modes, and operational mistakes encountered during development, along with the exact engineering corrections applied.

| # | Bug / Issue | Root Cause | Engineering Correction Applied |
| :-: | :--- | :--- | :--- |
| **1** | **Blank Cutoffs for Valid PDF Courses** *(e.g. E005 Telecommunication Round 2 showing blank instead of 722)* | **Course Row Duplication**: Canonicalizing branch names (e.g. mapping `Computer Science (AIML)` ➔ `AIML`) after data loading created duplicate course rows per college. 1-to-1 matcher assigned PDF cutoffs to row 1, leaving row 2 with blank `{}` cutoffs. | **Per-College Pre-Deduplication**: Aggregate intake/seats and merge duplicate course rows per institution **before** running PDF matching. Enforce composite uniqueness on `(college_id, canonical_course_name)`. |
| **2** | **Unmatched PDF Courses due to Line Breaks** | **PDF Text Extraction Artifacts**: Raw PDF extraction introduced internal space breaks (e.g. `ELECTRONICS AND TELECOMMUNICA TION`), causing fuzzy string similarity against `Telecommunication Engineering` to fall below the 0.75 threshold. | **Layout-Aware String Normalization**: Strip mid-word spacing artifacts and maintain explicit alias maps (`ELECTRONICS AND TELECOMMUNICATION` ↔ `Telecommunication Engineering`). |
| **3** | **Decimal Cutoff Display Distortion** *(e.g. 2457.5 rendered as 24575 or 2457)* | **String Truncation & Lossy Integer Parsing**: Removing commas/dots via regex or calling `parseInt()` converted floating-point ranks (e.g., `2457.5`) into integers or truncated strings. | **End-to-End Native Float Storage**: Store raw cutoffs as native `REAL/FLOAT` in database/JSON. Use a custom `formatCutoffRank()` formatter on frontend that preserves decimals while formatting integers with regional locale commas (`2,457.5`). |
| **4** | **Stale API Data Overwriting Fresh Data** | **Secondary Database Overwrite**: API router merged secondary relational SQL table rows over primary JSON dictionary data, replacing updated decimal floats with legacy integer values. | **Single-Source-of-Truth Priority**: Enforce non-destructive payload merging—relational tables may only append *missing* category keys, never overwrite primary JSON dictionary values. |
| **5** | **Special Quota Category Leakage** | **Lossy Quota Grouping**: Combining distinct special quota codes (`PH`, `D`, `DK`, `XD`) into generic categories caused cutoffs to render across incorrect courses. | **Strict Category Tagging**: Treat `PH`, `SNQ`, `GM`, `1G`, `2AG`, etc., as distinct, first-class category identifiers. Filter out categories that have no non-null values for the active context. |
| **6** | **UI Not Reflecting Code Updates** | **Browser Disk Caching**: Browser cached `app.js` and `seat_matrix_data_2026.json` static assets aggressively without checking the backend for changes. | **HTTP No-Cache Headers & Cache Busting**: Added FastAPI `Cache-Control: no-cache, no-store, must-revalidate` middleware and appended timestamp version tags (`app.js?v=20260907_170500`) to static script tags. |
| **7** | **SQLite Variable Limit Crash** | **Unbound `IN (...)` SQL Clauses**: Fetching details for 1,000+ courses in a single `WHERE id IN (...)` query breached SQLite's 999 parameter limit. | **Chunked SQL Batch Processing**: Slice parameter arrays into chunks of 300 items or fewer before executing parameter-bound SQL queries. |
| **8** | **2025 Decimal Cutoff Rank Distortion in Database Imports** *(e.g. 1126.75 inserted as 112675)* | **Regex Digit-Only Sanitization**: Database import script used `re.sub(r'[^\d]', '', str(rank))` during insertion, which stripped the decimal point `.` character (converting `1126.75` ➔ `112675`). | **Schema & Seeder Float Preservation**: Changed `cutoff_rank` schema type to `REAL` and updated database seeders to parse float strings directly preserving decimals (`1,126.75`). |
| **9** | **Illegible Small Fonts for Removed Courses/Colleges** | **Tiny Font & Hardcoded Truncation**: Using 11px font sizes with `white-space: nowrap; text-overflow: ellipsis` caused long course and college names to render truncated and unreadable on high-DPI screens. | **High-Contrast Responsive Badging**: Set font size to `13px` with `font-weight: 600`, `white-space: normal; word-break: break-word`, high-contrast color palette (`#f43f5e`), and expanded container max-height (`280px`). |
| **10** | **Renamed Institutions Flagged as False Positive "Removed"** | **Name-Only String Matching**: YoY structural shifts checked college names exclusively. Renamed institutions (e.g. `E063 SJM Institute` ➔ `SJM University`) were misclassified as removed. | **Dual Code & Name Matching**: Primary matching against unique institution code (`kea_code`) with name fallback to prevent false positive removals during institutional rebranding. |
| **11** | **Unexpected Syntax Error in Template Literal Interpolation** | **Function Declaration Inside Enclosing Function Scope**: Pasting a helper function declaration inside a template literal string within another function caused an unclosed template literal syntax error. | **Global Helper Function Scoping & Automated Syntax Validation**: Defined helper functions at outer top-level module scope and added pre-commit `node -c <file.js>` AST syntax validation. |

---

## 📊 Part II: Core Engineering & Architectural Guidelines

### 1. Data Extraction, Parsing & Numeric Precision

#### 1.1 Store Native Numeric Types (Avoid Early String Truncation)
* **Rule**: Cutoff ranks, scores, fees, and seat counts MUST be parsed and stored as native `INT` or `REAL/FLOAT` numeric types, never as raw unparsed strings or lossy integers.
* **Fractional Cutoffs**: Counseling bodies frequently issue fractional ranks (e.g., `2457.5`, `20319.5`). **NEVER** use `parseInt()` or `Math.round()` on raw cutoff strings, as this silently drops decimal values.
* **Non-Numeric Token Handling**: Raw PDF/table cells often contain non-numeric tokens (`--`, `ALLOTTED`, `EXTENDED`, `SATISFIED`, `N/A`). Parse these explicitly to `NULL`/`None` during ETL rather than throwing exceptions or assigning dummy `0` values.

```python
# ✅ CORRECT: Native Numeric Parser (ETL Phase)
def parse_cutoff_rank(val):
    if val is None or str(val).strip() in ("", "--", "—", "ALLOTTED", "EXTENDED", "N/A"):
        return None
    cleaned = str(val).replace(",", "").strip()
    try:
        f = float(cleaned)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None
```

#### 1.2 Robust Formatting Layer (Separation of Storage & Presentation)
* **Rule**: Keep raw numeric values in data stores and API payloads. Only apply locale formatting (e.g. thousand separators) in the UI presentation layer.
* **Custom Formatter**: Avoid generic `parseInt(val).toLocaleString()`. Implement a dedicated formatter that preserves decimal points while applying regional locale standards (e.g., `en-IN`).

```javascript
// ✅ CORRECT: Locale Formatter Preserving Fractional Ranks
function formatCutoffRank(val) {
  if (val === null || val === undefined || val === '' || val === '—') return '—';
  const numStr = String(val).trim().replace(/,/g, '');
  const num = parseFloat(numStr);
  if (isNaN(num)) return '—';

  if (Number.isInteger(num)) {
    return num.toLocaleString('en-IN');
  } else {
    const parts = numStr.split('.');
    const intPart = parseInt(parts[0], 10).toLocaleString('en-IN');
    return `${intPart}.${parts[1]}`;
  }
}
// formatCutoffRank(2457.5)  -> "2,457.5"
// formatCutoffRank(106260)  -> "1,06,260"
```

---

### 2. Data Matching & Disambiguation Architecture

#### 2.1 Pre-Deduplicate Courses Prior to External Dataset Matching
* **Rule**: Institutions MUST have clean, deduplicated course rows before running matching pipelines against external PDFs or seat matrix catalogs.
* **Aggregating Seats**: When merging duplicate rows resulting from branch canonicalization, sum intake/seat counts and merge non-null cutoff records.

#### 2.2 Enforce Strict 1-to-1 Course Matching Per Institution
* **The Problem**: Counseling PDFs and seat matrix catalogs often list similar branch names (e.g., `Artificial Intelligence & Machine Learning`, `Artificial Intelligence & Data Science`, and `Computer Science & Engineering (AIML)`). Greedy fuzzy matching can mistakenly map a single PDF cutoff entry to multiple courses in the same institution.
* **The Solution**: Enforce **strict 1-to-1 matching per college**. Once a PDF course entry is matched to an institutional course, mark it as used so it cannot be assigned to any sibling course.

```python
# ✅ CORRECT: Strict 1-to-1 Matching Per Institution
used_pdf_keys = set()
for course in college_courses:
    best_match = None
    best_score = 0.0
    for pdf_key, cutoffs in pdf_courses.items():
        if pdf_key in used_pdf_keys:
            continue
        score = calculate_similarity(course.name, pdf_key)
        if score > best_score:
            best_score = score
            best_match = pdf_key
            
    if best_match and best_score >= 0.75:
        used_pdf_keys.add(best_match)
        course.cutoffs = pdf_courses[best_match]
```

#### 2.3 Domain & Sub-Domain Negative Exclusion Rules
* **Rule**: Apply strict negative matching constraints to prevent cross-domain contamination.
  * `Data Science` MUST NOT match `Machine Learning`.
  * `Electronics & Communication` MUST NOT match `Telecommunication` or `Instrumentation`.
  * `Cyber Security` MUST NOT match `Blockchain` or `DevOps`.

---

### 3. Database & API Reliability

#### 3.1 PostgreSQL Primary with Lock-Free SQLite (WAL) Fallback Strategy
* **Rule**: Educational predictor portals should prioritize **PostgreSQL as the primary high-concurrency database** and automatically fall back to **lock-free SQLite (`WAL` mode)** if PostgreSQL is unavailable or unreachable.
* **Probing & Failover Optimization**: Use explicit connection timeouts (`connect_timeout=1`) when initializing the PostgreSQL connection pool. This ensures PostgreSQL is preferred by default, but if PostgreSQL is offline (e.g. during local developer execution or database maintenance), the backend switches to SQLite seamlessly within $\le 1$ second without throwing runtime errors.
* **Dialect Compatibility Layer**: Implement a database adapter that standardizes SQL query syntax across both PostgreSQL (`ILIKE`, `RETURNING id`, `%s`) and SQLite (`LIKE`, `lastrowid`, `?`).

```python
# ✅ CORRECT: PostgreSQL Primary with Automatic SQLite Fallback
@contextmanager
def get_db_cursor():
    pool = init_connection_pool()  # Tries PG on DB_HOST:DB_PORT with connect_timeout=1
    pg_conn = _get_healthy_pg_connection(pool) if pool else None

    if pg_conn:
        try:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
                pg_conn.commit()
        except Exception:
            pg_conn.rollback()
            raise
        finally:
            pool.putconn(pg_conn)
    else:
        # Fallback to WAL-mode SQLite
        with _get_sqlite_connection() as s_conn:
            yield SQLiteDictCursorAdapter(s_conn)
            s_conn.commit()
```

#### 3.2 Batch SQL Parameter Queries (Avoid Database Variable Limits)
* **Rule**: When executing `IN (...)` queries in SQLite or PostgreSQL, chunk parameter lists into batches of 300 items or fewer. SQLite throws an exception if `IN (...)` exceeds 999 parameters.

```python
# ✅ CORRECT: Chunked SQL Parameter Query
chunk_size = 300
all_courses = []
for i in range(0, len(college_ids), chunk_size):
    chunk = college_ids[i:i + chunk_size]
    placeholders = ", ".join(["%s"] * len(chunk))
    cur.execute(f"SELECT * FROM courses WHERE college_id IN ({placeholders})", tuple(chunk))
    all_courses.extend(cur.fetchall())
```

#### 3.2 Single Source of Truth & Safe API Merging
* **Rule**: When assembling API payloads from multiple data layers, preserve primary JSON dictionary values and DO NOT allow secondary legacy tables to overwrite primary data.

```python
# ✅ CORRECT: Non-Destructive Payload Assembly
for cut in relational_cutoffs:
    r, cat, val = cut["round"], cut["category"], cut["cutoff_rank"]
    target_dict = course[f"round{r}_cutoff"]
    # Only assign if category key is missing, never overwrite JSON floats with legacy ints
    if cat not in target_dict:
        target_dict[cat] = val
```

---

### 4. Frontend UI & Accessibility Standards

#### 4.1 Granular Multi-Category Subcategory Support
* **Rule**: Do not combine distinct legal quotas or subcategories into a single lossy dropdown option.
* **Separation**: Keep `PH` (Physically Handicapped), `D` (Differently Abled), `DK` (Differently Abled Kannada), and `XD` (Ex-Disabled) as **separate, first-class selectable categories**. Each code represents a distinct allotment matrix in state counseling.

#### 4.2 Categorized Dropdown Grouping (`<optgroup>`)
* **Rule**: When presenting long selection lists (e.g. 70+ engineering disciplines), group options into structured `<optgroup>` categories with emoji identifiers instead of displaying a flat list.

```html
<!-- ✅ CORRECT: Grouped Select Element -->
<select id="course-filter">
  <option value="">All Courses</option>
  <optgroup label="💻 Computer Science & IT">
    <option value="Computer Science and Engineering">Computer Science and Engineering</option>
    <option value="Artificial Intelligence and Machine Learning">Artificial Intelligence and Machine Learning</option>
  </optgroup>
  <optgroup label="⚡ Electronics & Electrical">
    <option value="Electronics and Communication Engineering">Electronics and Communication Engineering</option>
  </optgroup>
</select>
```

---

### 5. Cache Management & Deployment Protocol

#### 5.1 Server-Side HTTP No-Cache Headers
* **Rule**: Middleware serving static assets (`.js`, `.css`, `.html`, `.json`) and API endpoints MUST emit explicit Cache-Control headers to prevent stale browser disk caching.

```python
# ✅ CORRECT: FastAPI No-Cache Middleware
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        path = request.url.path.lower()
        if path.endswith((".html", ".js", ".css", ".json")) or path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
```

#### 5.2 Timestamped Asset Versioning
* **Rule**: Always append a timestamp or commit hash version tag to static script tags in HTML files.

```html
<!-- ✅ CORRECT: Versioned Script Tag -->
<script src="app_v4.js?v=20260907_170500"></script>
```

---

## 🏆 Part III: Quality Assurance & Pre-Flight Checklist

Use this pre-flight checklist prior to releasing updates or launching any new predictor application:

| Phase | Check Item | Status |
| :--- | :--- | :---: |
| **ETL & Data** | Preserve fractional cutoffs (`2457.5`) as native floats; eliminate lossy `parseInt()` | ✅ Verified |
| **ETL & Data** | Pre-deduplicate courses per institution before running fuzzy PDF matchers | ✅ Verified |
| **ETL & Data** | Apply PDF layout line-break stripping (`TELECOMMUNICA TION`) and domain exclusion rules | ✅ Verified |
| **Backend API** | Chunk SQL `IN (...)` parameters into batches of $\le 300$ to prevent SQLite crashes | ✅ Verified |
| **Backend API** | Enforce single-source-of-truth priority so secondary SQL tables don't overwrite JSON floats | ✅ Verified |
| **Frontend UI** | Format ranks with `formatCutoffRank()` preserving decimals and adding regional commas | ✅ Verified |
| **Frontend UI** | Keep `PH`, `SNQ`, `GM`, `1G`, `2AG`, etc., as distinct selectable categories | ✅ Verified |
| **Frontend UI** | Group 70+ course options into structured `<optgroup>` categories | ✅ Verified |
| **Deployment** | Enable `Cache-Control: no-cache` middleware and timestamp script tags (`app.js?v=TIMESTAMP`) | ✅ Verified |
