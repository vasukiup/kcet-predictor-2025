import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.agent import run_agent
import uvicorn

app = FastAPI(title="KCET Predictor AI Agent Backend")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Mount static files from root directory
# E.g. index.html, app_v4.js, style_v4.css, seat_matrix_data.json
# Note: Mount at "/" should be last
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
