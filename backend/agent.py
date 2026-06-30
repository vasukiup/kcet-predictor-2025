import os
import sqlite3
import re
import json
import urllib.request
import urllib.error

# Load environment variables from .env file if it exists
def load_dotenv():
    env_path = os.path.join("backend", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_dotenv()

# System prompt defining schema and loop
SYSTEM_PROMPT = """You are a highly knowledgeable KCET (Karnataka Common Entrance Test) Admission AI Agent.
Your job is to answer user queries about engineering colleges, course intakes, seat matrices, special category seats, and round-wise cutoffs for 2025.

You have access to a SQLite database 'backend/kcet.db' with the following schema:

1. colleges:
   - id (INTEGER PRIMARY KEY)
   - college_number (INTEGER) -- The KEA college code (e.g. 3, 48, etc.)
   - college_name (TEXT)
   - address (TEXT)
   - annexure (TEXT) -- E.g. 'A', 'B', 'C', 'D', 'M', 'O', 'P', 'Z'
   - college_type (TEXT) -- E.g. 'Private Unaided Engineering Colleges'
   - district (TEXT)
   - total_intake (INTEGER)
   - total_kea_seats (INTEGER)

2. courses:
   - id (INTEGER PRIMARY KEY)
   - college_id (INTEGER, FK to colleges.id)
   - course_name (TEXT)
   - total_intake (INTEGER)
   - total_kea_seats (INTEGER)
   - snq_5pct (INTEGER)
   - kea_ph (INTEGER), kea_spl (INTEGER), kea_hk (INTEGER), kea_rk (INTEGER), kea_tot (INTEGER)
   - cat2_seats (INTEGER) -- COMEDK seats
   - cat3_seats (INTEGER) -- Management seats
   - over_above_5pct (INTEGER)
   - sports, ncc, sct_guides, defence, k_defence, ex_defence, capf, ai, xcapf, tot_special_seats (INTEGER) -- Special category seats

3. cutoffs:
   - id (INTEGER PRIMARY KEY)
   - course_id (INTEGER, FK to courses.id)
   - round (INTEGER) -- E.g. 1, 2, or 3
   - category (TEXT) -- E.g. 'GM', 'GMK', 'GMR', '1G', '2AG', '3AG', 'SCG', 'STG', etc.
   - cutoff_rank (INTEGER) -- The rank cutoff

RULES FOR QUERYING:
- To answer the question, you can write and execute SQL queries.
- Output your SQL query wrapped in a code block:
```sql
SELECT ...
```
- Wait for the query results. Only output ONE SQL query block at a time.
- If you have all the information, output your final answer directly to the user in a helpful, friendly format (markdown).
- Be careful with course names and college names: use LIKE '%name%' for fuzzy matching.
- Always fetch the college name, code, course name, and cutoff rank/fees when providing comparisons.
"""

def execute_sql(sql_query):
    db_path = os.path.join("backend", "kcet.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(row) for row in rows[:50]] # Limit to 50 results
        conn.close()
        return {"columns": columns, "rows": results}
    except Exception as e:
        return {"error": str(e)}

def call_gemini_api(messages):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Format messages for Gemini API
    contents = []
    for msg in messages:
        role = msg["role"]
        # Gemini roles: user, model
        gemini_role = "user" if role in ("user", "system") else "model"
        
        contents.append({
            "role": gemini_role,
            "parts": [{"text": msg["content"]}]
        })
        
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            candidates = res_data.get("candidates", [])
            if candidates:
                text = candidates[0]["content"]["parts"][0]["text"]
                return text
    except urllib.error.HTTPError as e:
        print(f"Gemini API HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Gemini API Error: {e}")
    return None

def run_agent(user_query, chat_history=None):
    if chat_history is None:
        chat_history = []
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Return mock / helper message when key is not configured
        mock_reply = (
            "⚠️ **Gemini API Key not set!**\n\n"
            "Please add your key in `backend/.env` file:\n"
            "```env\nGEMINI_API_KEY=your_actual_api_key_here\n```\n"
            "Here is a mock response to your query:\n\n"
            f"**Query**: \"{user_query}\"\n\n"
            "*(Mock Agent)*: You asked about admission chances. Once you configure the API key, the agent will query the SQLite database (`backend/kcet.db`) and give you exact cut-offs and predictions!"
        )
        return {
            "reply": mock_reply,
            "sql_queries": []
        }
        
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    # Append recent chat history (limit to last 10 messages)
    for h in chat_history[-10:]:
        messages.append({"role": h["role"], "content": h["content"]})
        
    messages.append({"role": "user", "content": user_query})
    
    executed_queries = []
    loop_count = 0
    max_loops = 5
    
    while loop_count < max_loops:
        loop_count += 1
        model_reply = call_gemini_api(messages)
        if not model_reply:
            return {
                "reply": "I'm sorry, I encountered an error communicating with the AI model. Please check your API key and connection.",
                "sql_queries": executed_queries
            }
            
        # Check if the model output a SQL query
        sql_match = re.search(r'```sql\s*(.*?)\s*```', model_reply, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql_query = sql_match.group(1).strip()
            print(f"Agent SQL Query: {sql_query}")
            
            # Execute SQL
            results = execute_sql(sql_query)
            executed_queries.append({
                "query": sql_query,
                "results": results
            })
            
            # Feed back to model
            messages.append({"role": "model", "content": model_reply})
            results_str = json.dumps(results, indent=2)
            messages.append({"role": "user", "content": f"Database results:\n```json\n{results_str}\n```"})
        else:
            # Final reply reached
            return {
                "reply": model_reply,
                "sql_queries": executed_queries
            }
            
    return {
        "reply": "I reached my reasoning limit trying to answer your query. Here is what I gathered: " + model_reply,
        "sql_queries": executed_queries
    }
