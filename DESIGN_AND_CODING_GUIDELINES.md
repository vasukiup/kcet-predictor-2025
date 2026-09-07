# System Design & Coding Guidelines
**Comprehensive Engineering Best Practices for Educational & Counseling Predictor Applications**

---

## 📌 Executive Summary

This document synthesizes key architectural principles, data engineering standards, frontend patterns, and backend reliability protocols established while building the **KEA Seat Matrix & Cutoff Prediction Portal**. 

It serves as a reusable blueprint for building similar data-heavy portal applications (such as NEET, JOSAIA/CSAB, COMEDK, or state-level counseling predictors).

---

## 1. 📊 Data Extraction, Parsing & Numeric Precision

### 1.1 Store Native Numeric Types (Avoid Early String Truncation)
* **Rule**: Cutoff ranks, scores, fees, and seat counts MUST be parsed and stored as native `INT` or `REAL/FLOAT` numeric types, never as raw unparsed strings or lossy integers.
* **Fractional Cutoffs**: Counseling bodies frequently issue fractional ranks (e.g., `2457.5`, `20319.5`). **NEVER** use `parseInt()` or `Math.round()` on raw cutoff strings, as this silently drops decimal values (converting `2457.5` to `2457` or `24575`).
* **Non-Numeric Token Handling**: Raw PDF/table cells often contain non-numeric tokens (`--`, `ALLOTTED`, `EXTENDED`, `SATISFIED`, `N/A`). Parse these explicitly to `NULL`/`None` during ETL rather than throwing exceptions or assigning dummy `0` values.

```python
# ✅ CORRECT: Native Numeric Parser (ETL Phase)
def parse_cutoff_rank(val):
    if val is None or str(val).strip() in ("", "--", "—", "ALLOTTED", "EXTENDED"):
        return None
    cleaned = str(val).replace(",", "").strip()
    try:
        f = float(cleaned)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None
```

---

### 1.2 Robust Formatting Layer (Separation of Storage & Presentation)
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
// formatCutoffRank(2457.5) -> "2,457.5"
// formatCutoffRank(106260) -> "1,06,260"
```

---

## 2. 🧩 Data Matching & Disambiguation Architecture

### 2.1 Enforce Strict 1-to-1 Course Matching Per Institution
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

---

### 2.2 Domain & Sub-Domain Negative Exclusion Rules
* **Rule**: Apply strict negative matching constraints to prevent cross-domain contamination.
  * `Data Science` MUST NOT match `Machine Learning`.
  * `Electronics & Communication` MUST NOT match `Telecommunication` or `Instrumentation`.
  * `Cyber Security` MUST NOT match `Blockchain` or `DevOps`.

---

## 3. 🗄️ Database & API Reliability

### 3.1 Batch SQL Parameter Queries (Avoid Database Variable Limits)
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

---

### 3.2 Single Source of Truth & Safe API Merging
* **Rule**: When assembling API payloads from multiple database tables (e.g. `courses` table JSON strings vs `cutoffs` relational table rows), preserve primary JSON dictionary values and DO NOT allow secondary legacy tables to overwrite primary data.

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

## 4. 🎨 Frontend UI & Accessibility Standards

### 4.1 Granular Multi-Category Subcategory Support
* **Rule**: Do not combine distinct legal quotas or subcategories into a single lossy dropdown option.
* **Separation**: Keep `PH` (Physically Handicapped), `D` (Differently Abled), `DK` (Differently Abled Kannada), and `XD` (Ex-Disabled) as **separate, first-class selectable categories**. Each code represents a distinct allotment matrix in state counseling.

---

### 4.2 Categorized Dropdown Grouping (`<optgroup>`)
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

## 5. ⚡ Cache Management & Deployment Protocol

### 5.1 Server-Side HTTP No-Cache Headers
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

---

### 5.2 Timestamped Asset Versioning
* **Rule**: Always append a timestamp or commit hash version tag to static script tags in HTML files.

```html
<!-- ✅ CORRECT: Versioned Script Tag -->
<script src="app_v4.js?v=20260907_170500"></script>
```

---

## 6. 🏆 Summary Checklist for Future Counseling Applications

| Phase | Engineering Requirement | Status |
| :--- | :--- | :---: |
| **ETL & Data** | Preserve fractional cutoffs (`2457.5`) as native floats/reals; avoid `parseInt` truncation | ✅ Enforced |
| **ETL & Data** | Implement strict 1-to-1 course matching per institution with negative domain exclusions | ✅ Enforced |
| **Backend API** | Chunk SQL `IN (...)` parameters into batches of <= 300 to prevent database limit crashes | ✅ Enforced |
| **Backend API** | Prevent secondary relational tables from overwriting JSON dictionary primary cutoffs | ✅ Enforced |
| **Frontend UI** | Format numbers with custom `formatCutoffRank()` for regional locale thousand separators | ✅ Enforced |
| **Frontend UI** | Separate `PH`, `D`, `DK`, `XD` and special categories into distinct first-class dropdown lookups | ✅ Enforced |
| **Frontend UI** | Group 70+ course options into structured `<optgroup>` categories | ✅ Enforced |
| **Deployment** | Enforce `No-Cache` HTTP headers and timestamped script version tags (`app.js?v=TIMESTAMP`) | ✅ Enforced |
