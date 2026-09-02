# =======================================================
# Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
# Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
# Application: KEA Seat Matrix & Prediction Portal Launcher
# =======================================================
import os
import sys
import time
import webbrowser
import subprocess

def main():
    print("=" * 60)
    print(" 🚀 KEA Seat Matrix & Prediction Portal Launcher")
    print("=" * 60)
    
    # Ensure current working directory is the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    url = "http://127.0.0.1:8000"
    print(f"\n[1/2] Opening browser at {url}...")
    webbrowser.open(url)
    
    print("\n[2/2] Starting backend FastAPI server on http://127.0.0.1:8000...")
    print("Press Ctrl+C in this window at any time to stop the server.\n")
    
    try:
        import uvicorn
        uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
    except ImportError:
        print("uvicorn is not installed in current Python environment. Running via python -m uvicorn...")
        subprocess.run([sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])

if __name__ == "__main__":
    main()
