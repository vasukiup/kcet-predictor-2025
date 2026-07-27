# =======================================================
# Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
# Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
# Application: KEA Seat Matrix & Prediction Portal
# =======================================================
import os
import base64
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io
import csv
import json

from backend.agent import run_agent, load_dotenv
from backend.database import get_db_cursor

# Ensure environment variables are loaded
load_dotenv()

# Global Basic Auth Middleware
class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Expose custom username and password from environment (default: admin / kcet2025)
        username = os.environ.get("PORTAL_USERNAME", "admin")
        password = os.environ.get("PORTAL_PASSWORD", "kcet2025")
        
        # Bypass healthcheck or docs if needed, otherwise secure everything
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return Response(
                "Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": "Basic realm='KCET Predictor Portal'"}
            )
            
        try:
            auth_type, encoded_creds = auth_header.split(" ", 1)
            decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
            req_username, req_password = decoded_creds.split(":", 1)
            if req_username == username and req_password == password:
                return await call_next(request)
        except Exception:
            pass
            
        return Response(
            "Unauthorized",
            status_code=401,
            headers={"WWW-Authenticate": "Basic realm='KCET Predictor Portal'"}
        )

app = FastAPI(title="KCET Predictor AI Agent Backend")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply global authentication middleware
app.add_middleware(BasicAuthMiddleware)


# ────────────────────────────────────────────────────────
# AUDIT LOGGING HELPER
# ────────────────────────────────────────────────────────

def log_activity(username: str, action: str, details: str = None, ip_address: str = None):
    """
    Inserts a row into the audit_logs table.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO audit_logs (username, action, details, ip_address)
                VALUES (%s, %s, %s, %s)
            """, (username, action, details, ip_address))
    except Exception as e:
        print(f"Error logging activity '{action}' for '{username}': {e}")


# ────────────────────────────────────────────────────────
# AUTHENTICATION SCHEMAS & ROUTES
# ────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str
    rank: Optional[int] = None
    category: Optional[str] = None
    region: Optional[str] = None

class UserLogin(BaseModel):
    username_or_email: str
    password: str
    role: str

@app.post("/api/auth/register")
async def register_user(user: UserRegister, request: Request):
    try:
        with get_db_cursor() as cur:
            # Check if email or username already exists
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user.username, user.email))
            exists = cur.fetchone()
            if exists:
                raise HTTPException(status_code=400, detail="Username or email is already registered.")
            
            cur.execute("""
                INSERT INTO users (username, email, password, role, rank, category, region)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user.username, user.email, user.password, user.role.lower(), user.rank, user.category, user.region))
        
        # Log registration activity
        client_ip = request.client.host if request.client else "unknown"
        log_activity(user.username, "REGISTER", f"Role: {user.role}, Email: {user.email}, Rank: {user.rank}", client_ip)
        return {"status": "success", "message": f"User {user.username} registered successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/api/auth/login")
async def login_user(user: UserLogin, request: Request):
    try:
        client_ip = request.client.host if request.client else "unknown"
        role_lower = user.role.lower()

        if role_lower == 'student':
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT username, email, rank, category, region 
                    FROM users 
                    WHERE (username = %s OR email = %s) AND password = %s AND role = 'student'
                """, (user.username_or_email, user.username_or_email, user.password))
                db_user = cur.fetchone()
                if not db_user:
                    raise HTTPException(status_code=401, detail="Invalid student email/username or password.")
                
                # Log login activity
                log_activity(db_user["username"], "LOGIN", f"Role: student (DB)", client_ip)
                return {
                    "status": "success", 
                    "user": {
                        "name": db_user["username"],
                        "email": db_user["email"],
                        "role": "student",
                        "rank": db_user["rank"],
                        "category": db_user["category"],
                        "region": db_user["region"]
                    }
                }
        else:
            # Predefined staff credentials checks
            if role_lower == 'superuser':
                if user.username_or_email == 'superuser' and user.password == 'kcet2025':
                    log_activity("Global Admin", "LOGIN", "Role: superuser", client_ip)
                    return {"status": "success", "user": {"name": "Global Admin", "role": "superuser"}}
            elif role_lower == 'authority':
                if user.username_or_email == 'authority' and user.password == 'kcet2025':
                    log_activity("KEA Admin Console", "LOGIN", "Role: authority", client_ip)
                    return {"status": "success", "user": {"name": "KEA Admin Console", "role": "authority"}}
            elif role_lower == 'counsellor':
                if user.username_or_email == 'counsellor' and user.password == 'kcet2025':
                    log_activity("Professional Advisor", "LOGIN", "Role: counsellor", client_ip)
                    return {"status": "success", "user": {"name": "Professional Advisor", "role": "counsellor"}}
            elif role_lower == 'institution':
                # Check correct group id and password kcet2025
                groups = ['rvgroup', 'bmsgroup', 'pesgroup', 'dsgroup']
                if user.username_or_email in groups and user.password == 'kcet2025':
                    gname = user.username_or_email.upper()
                    log_activity(f"{gname} Admin", "LOGIN", f"Role: institution, Group: {user.username_or_email}", client_ip)
                    return {"status": "success", "user": {"name": f"{gname} Admin", "role": "institution", "institutionGroup": user.username_or_email}}
            
            raise HTTPException(status_code=401, detail="Invalid credentials for staff role.")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LogRequest(BaseModel):
    username: str
    action: str
    details: Optional[str] = None

@app.post("/api/log")
async def log_client_activity(req: LogRequest, request: Request):
    try:
        client_ip = request.client.host if request.client else "unknown"
        log_activity(req.username, req.action, req.details, client_ip)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/activities")
async def get_admin_activities(year: int = 2026):
    """
    Returns aggregated metrics from users and audit_logs tables for the admin console.
    """
    try:
        with get_db_cursor() as cur:
            # 1. Total registered users count by role
            cur.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
            registrations = {row["role"]: row["count"] for row in cur.fetchall()}

            # Ensure default keys exist
            for r in ["student", "counsellor", "institution", "authority", "superuser"]:
                if r not in registrations:
                    registrations[r] = 0

            # 2. Action breakdown count
            cur.execute("SELECT action, COUNT(*) as count FROM audit_logs GROUP BY action")
            action_stats = {row["action"]: row["count"] for row in cur.fetchall()}

            for act in ["REGISTER", "LOGIN", "PREDICTION", "OPTION_OPTIMIZE", "DOWNLOAD", "COMPARE"]:
                if act not in action_stats:
                    action_stats[act] = 0

            # 3. Recent 50 audit logs
            cur.execute("""
                SELECT id, username, action, details, ip_address, 
                       TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') as time_str 
                FROM audit_logs 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            recent_logs = cur.fetchall()

            return {
                "registrations": registrations,
                "action_stats": action_stats,
                "recent_logs": recent_logs
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ────────────────────────────────────────────────────────
# DATABASE-BACKED API ENDPOINTS
# ────────────────────────────────────────────────────────

@app.get("/api/filters")
async def get_filters(year: int = 2026):
    """
    Returns unique courses, districts, and college types for filtering.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT DISTINCT course_name FROM courses WHERE year = %s ORDER BY course_name", (year,))
            courses = [row["course_name"] for row in cur.fetchall()]

            cur.execute("SELECT DISTINCT district FROM colleges WHERE year = %s AND district IS NOT NULL AND district != '' ORDER BY district", (year,))
            districts = [row["district"] for row in cur.fetchall()]

            cur.execute("SELECT DISTINCT college_type FROM colleges WHERE year = %s AND college_type IS NOT NULL AND college_type != '' ORDER BY college_type", (year,))
            types = [row["college_type"] for row in cur.fetchall()]

            return {
                "courses": courses,
                "districts": districts,
                "types": types
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/colleges")
async def get_colleges(
    year: int = 2026,
    q: str = "",
    annexure: str = "all",
    district: str = "",
    course: str = "",
    min_seats: int = 0,
    affiliation: str = "",
    naac: str = "",
    nba: str = "",
    min_salary: float = 0.0,
    max_hostel: int = 150000,
    limit: int = 30,
    offset: int = 0
):
    """
    Searches, filters, and returns paginated colleges and course totals from PostgreSQL.
    """
    try:
        with get_db_cursor() as cur:
            conditions = ["col.year = %s"]
            params = [year]

            if q:
                conditions.append("(col.college_name ILIKE %s OR col.address ILIKE %s OR col.kea_code ILIKE %s)")
                q_param = f"%{q}%"
                params.extend([q_param, q_param, q_param])

            if annexure != "all":
                conditions.append("col.annexure = %s")
                params.append(annexure)
            if district:
                conditions.append("col.district = %s")
                params.append(district)
            if min_seats > 0:
                conditions.append("col.total_intake >= %s")
                params.append(min_seats)
            if affiliation:
                conditions.append("col.affiliation ILIKE %s")
                params.append(f"%{affiliation}%")
            if naac:
                conditions.append("col.naac_grade ILIKE %s")
                params.append(f"%{naac}%")
            if nba:
                conditions.append("col.nba_accredited ILIKE %s")
                params.append(f"%{nba}%")

            if min_salary > 0:
                conditions.append("CAST(NULLIF(REGEXP_REPLACE(col.placements_avg_package, '[^0-9.]', '', 'g'), '') AS NUMERIC) >= %s")
                params.append(min_salary)

            if max_hostel < 150000:
                conditions.append("CAST(NULLIF(REGEXP_REPLACE(col.hostel_fees, '[^0-9]', '', 'g'), '') AS INTEGER) <= %s")
                params.append(max_hostel)

            join_clause = ""
            if course:
                join_clause = "JOIN courses cr ON col.id = cr.college_id"
                conditions.append("cr.course_name = %s")
                params.append(course)

            where_clause = " WHERE " + " AND ".join(conditions)

            count_query = f"SELECT COUNT(DISTINCT col.id) as count, COALESCE(SUM(col.total_kea_seats), 0) as total_seats FROM colleges col {join_clause} {where_clause}"
            cur.execute(count_query, tuple(params))
            stats = cur.fetchone()
            total_count = stats["count"]
            total_seats = stats["total_seats"]

            col_query = f"""
                SELECT DISTINCT 
                    col.id, col.college_number, col.kea_code, col.college_name, col.address,
                    col.annexure, col.college_type, col.district, col.total_intake, col.total_kea_seats,
                    col.established_year, col.nirf_rank, col.naac_grade, col.nba_accredited,
                    col.placements_avg_package, col.placements_highest_package, col.placements_rate,
                    col.hostel_fees, col.hostel_capacity, col.hostel_mess_included, col.campus_size,
                    col.campus_majestic_dist_km, col.campus_nearest_transit
                FROM colleges col
                {join_clause}
                {where_clause}
                ORDER BY col.college_name ASC
                LIMIT %s OFFSET %s
            """
            cur.execute(col_query, tuple(params + [limit, offset]))
            colleges = cur.fetchall()

            if not colleges:
                return {
                    "colleges": [],
                    "total_count": total_count,
                    "total_seats": total_seats
                }

            college_ids = [col["id"] for col in colleges]
            
            # Fetch all courses for these colleges in one query
            placeholders = ", ".join(["%s"] * len(college_ids))
            cur.execute(f"""
                SELECT 
                    id, college_id, course_name, total_intake, total_kea_seats, snq_5pct,
                    kea_ph, kea_spl, kea_hk, kea_rk, kea_tot, cat2_seats, cat3_seats,
                    over_above_5pct, sports, ncc, sct_guides, defence, k_defence, ex_defence, capf, ai, xcapf, tot_special_seats,
                    placements_min_package, placements_avg_package, placements_max_package, placements_rate, placements_industry, placements_recruiters
                FROM courses 
                WHERE college_id IN ({placeholders}) AND year = %s
            """, tuple(college_ids + [year]))
            all_courses = cur.fetchall()

            course_ids = [cr["id"] for cr in all_courses]
            
            # Map college_id -> list of courses
            courses_by_college = {}
            for cr in all_courses:
                cid = cr["college_id"]
                if cid not in courses_by_college:
                    courses_by_college[cid] = []
                courses_by_college[cid].append(cr)

            # Fetch all cutoffs for these courses in one query
            cutoffs_by_course = {}
            if course_ids:
                course_placeholders = ", ".join(["%s"] * len(course_ids))
                cur.execute(f"""
                    SELECT course_id, round, category, cutoff_rank 
                    FROM cutoffs 
                    WHERE course_id IN ({course_placeholders}) AND year = %s
                """, tuple(course_ids + [year]))
                all_cutoffs = cur.fetchall()
                
                for cut in all_cutoffs:
                    crid = cut["course_id"]
                    if crid not in cutoffs_by_course:
                        cutoffs_by_course[crid] = []
                    cutoffs_by_course[crid].append(cut)

            # Nest them in python
            for col in colleges:
                cid = col["id"]
                col["courses"] = courses_by_college.get(cid, [])
                for cr in col["courses"]:
                    crid = cr["id"]
                    cutoffs = cutoffs_by_course.get(crid, [])
                    cr["mock_round1_cutoff"] = {}
                    cr["round1_cutoff"] = {}
                    cr["round2_cutoff"] = {}
                    cr["round3_cutoff"] = {}
                    for cut in cutoffs:
                        r = cut["round"]
                        cat = cut["category"]
                        val = cut["cutoff_rank"]
                        if r == 0:
                            cr["mock_round1_cutoff"][cat] = val
                        elif r == 1:
                            cr["round1_cutoff"][cat] = val
                        elif r == 2:
                            cr["round2_cutoff"][cat] = val
                        elif r == 3:
                            cr["round3_cutoff"][cat] = val

            return {
                "colleges": colleges,
                "total_count": total_count,
                "total_seats": total_seats
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/predictor")
async def get_predictions(
    rank: int,
    category: str,
    round_val: int = 1,
    course_name: str = "",
    year: int = 2026,
    username: str = "guest",
    request: Request = None
):
    """
    Predicts course allotment chances and logs the event to audit logs.
    """
    try:
        # Audit log prediction
        client_ip = request.client.host if request and request.client else "unknown"
        log_activity(
            username, 
            "PREDICTION", 
            f"Rank: {rank}, Category: {category}, Round: {round_val}, Course: {course_name or 'All'}", 
            client_ip
        )

        with get_db_cursor() as cur:
            conditions = [
                "cut.year = %s",
                "cut.round = %s",
                "cut.category = %s",
                "cut.cutoff_rank >= %s"
            ]
            params = [year, round_val, category, rank - 3000]

            if course_name:
                conditions.append("cr.course_name = %s")
                params.append(course_name)

            where_clause = " WHERE " + " AND ".join(conditions)

            query = f"""
                SELECT 
                    col.college_name,
                    col.college_number,
                    col.kea_code,
                    col.annexure,
                    cr.course_name,
                    cr.total_intake,
                    cr.total_kea_seats,
                    cut.cutoff_rank
                FROM cutoffs cut
                JOIN courses cr ON cut.course_id = cr.id
                JOIN colleges col ON cr.college_id = col.id
                {where_clause}
                ORDER BY cut.cutoff_rank ASC
                LIMIT 100
            """
            cur.execute(query, tuple(params))
            predictions = cur.fetchall()

            return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/compare")
async def get_compare_colleges(
    ids: List[int] = Query(...), 
    year: int = 2026, 
    username: str = "guest",
    request: Request = None
):
    """
    Compares colleges side-by-side and logs the compare event.
    """
    try:
        client_ip = request.client.host if request and request.client else "unknown"
        log_activity(username, "COMPARE", f"Colleges compared IDs: {ids}", client_ip)

        with get_db_cursor() as cur:
            placeholders = ", ".join(["%s"] * len(ids))
            query = f"""
                SELECT 
                    id, college_number, kea_code, college_name, address,
                    annexure, college_type, district, total_intake, total_kea_seats,
                    established_year, nirf_rank, naac_grade, nba_accredited,
                    placements_avg_package, placements_highest_package, placements_rate,
                    hostel_fees, hostel_capacity, hostel_mess_included, campus_size,
                    campus_majestic_dist_km, col.campus_nearest_transit
                FROM colleges col
                WHERE id IN ({placeholders}) AND year = %s
            """
            cur.execute(query, tuple(ids + [year]))
            colleges = cur.fetchall()

            for col in colleges:
                cur.execute("""
                    SELECT course_name, total_intake, total_kea_seats, placements_avg_package, placements_rate
                    FROM courses 
                    WHERE college_id = %s AND year = %s
                """, (col["id"], year))
                col["courses"] = cur.fetchall()

            return colleges
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/stats")
async def get_aggregate_stats(year: int = 2026):
    """
    Aggregates metrics directly from the DB for charts and statistics.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT annexure, SUM(total_kea_seats) as seats FROM colleges WHERE year = %s GROUP BY annexure", (year,))
            by_annexure = cur.fetchall()

            cur.execute("SELECT district, SUM(total_kea_seats) as seats FROM colleges WHERE year = %s AND district IS NOT NULL GROUP BY district ORDER BY seats DESC LIMIT 10", (year,))
            by_district = cur.fetchall()

            cur.execute("SELECT course_name, SUM(total_intake) as intake FROM courses WHERE year = %s GROUP BY course_name ORDER BY intake DESC LIMIT 15", (year,))
            by_course = cur.fetchall()

            cur.execute("SELECT SUM(total_kea_seats) as kea, SUM(cat2_seats) as comedk, SUM(cat3_seats) as mgmt FROM courses WHERE year = %s", (year,))
            quota_sums = cur.fetchone()

            cur.execute("SELECT year, SUM(total_intake) as total_intake, SUM(total_kea_seats) as kea_seats, COUNT(DISTINCT id) as colleges FROM colleges GROUP BY year ORDER BY year DESC")
            yoy_compare = cur.fetchall()

            return {
                "by_annexure": by_annexure,
                "by_district": by_district,
                "by_course": by_course,
                "quota_sums": quota_sums,
                "yoy_compare": yoy_compare
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/downloads")
async def download_data(
    year: int = 2026,
    annexure: str = "all",
    district: str = "",
    course: str = "",
    min_seats: int = 0,
    format: str = "csv",
    username: str = "admin",
    request: Request = None
):
    """
    Generates downloads and logs the download event.
    """
    try:
        client_ip = request.client.host if request and request.client else "unknown"
        log_activity(username, "DOWNLOAD", f"Year: {year}, Format: {format}, Scope: {annexure}/{district}", client_ip)

        with get_db_cursor() as cur:
            conditions = ["col.year = %s"]
            params = [year]

            if annexure != "all":
                conditions.append("col.annexure = %s")
                params.append(annexure)
            if district:
                conditions.append("col.district = %s")
                params.append(district)
            if min_seats > 0:
                conditions.append("col.total_intake >= %s")
                params.append(min_seats)

            join_clause = ""
            if course:
                join_clause = "JOIN courses cr ON col.id = cr.college_id"
                conditions.append("cr.course_name = %s")
                params.append(course)

            where_clause = " WHERE " + " AND ".join(conditions)

            query = f"""
                SELECT 
                    col.college_number, col.kea_code, col.college_name, col.annexure, col.district, col.total_kea_seats
                FROM colleges col
                {join_clause}
                {where_clause}
                ORDER BY col.college_name ASC
            """
            cur.execute(query, tuple(params))
            records = cur.fetchall()

            if format == "json":
                return StreamingResponse(
                    io.BytesIO(json.dumps(records, indent=2).encode("utf-8")),
                    media_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename=kcet_matrix_{year}.json"}
                )

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["College Number", "KEA Code", "College Name", "Annexure", "District", "KEA Seats"])
            for row in records:
                writer.writerow([row["college_number"], row["kea_code"], row["college_name"], row["annexure"], row["district"], row["total_kea_seats"]])

            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode("utf-8")),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=kcet_matrix_{year}.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ────────────────────────────────────────────────────────
# AGENT CHAT ENDPOINT
# ────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        chat_history = [{"role": msg.role, "content": msg.content} for msg in req.history]
        result = run_agent(req.message, chat_history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files from root directory last
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
