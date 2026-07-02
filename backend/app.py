import os
import base64
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import BaseModel
from typing import List, Optional
from backend.agent import run_agent, load_dotenv
import uvicorn

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
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting secure server on port {port}...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
