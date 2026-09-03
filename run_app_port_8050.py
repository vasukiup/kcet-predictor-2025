import subprocess
import webbrowser
import time
import sys
import os

def launch():
    print("==================================================")
    print("  KCET 2026 Portal Launcher - PORT 8050")
    print("==================================================")
    
    url = "http://127.0.0.1:8050"
    print(f"Starting FastAPI backend server on {url}...")
    
    # Launch uvicorn on port 8050
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8050"]
    proc = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    time.sleep(2)
    print(f"Opening default web browser to {url}...")
    webbrowser.open(url)
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("Stopping server...")
        proc.terminate()

if __name__ == '__main__':
    launch()
