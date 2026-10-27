"""
CyberMind AI - Master Application Launcher
Launches the CyberMind AI React frontend and FastAPI backend.
"""

from __future__ import annotations

import os
import sys
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BANNER = r"""
   _____      _               __  __ _           _         _    ___ 
  / ____|    | |             |  \/  (_)         | |       / \  |_ _|
 | |    _   _| |__   ___ _ __| \  / |_ _ __   __| |      / _ \  | | 
 | |   | | | | '_ \ / _ \ '__| |\/| | | '_ \ / _` |     / ___ \ | | 
 | |___| |_| | |_) |  __/ |  | |  | | | | | | (_| |    / /   \ \| | 
  \_____\__, |_.__/ \___|_|  |_|  |_|_|_| |_|\__,_|   /_/     \_|___|
         __/ |                                                      
        |___/        Enterprise Cybersecurity Intelligence Platform
"""

def main():
    parser = argparse.ArgumentParser(description="Launch CyberMind AI")
    parser.add_argument("--dev", action="store_true", help="Launch in development mode (Vite dev server + FastAPI reload)")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host address")
    parser.add_argument("--port", type=int, default=8000, help="Backend port")
    args = parser.parse_args()

    print(BANNER)
    print(f"[*] Starting CyberMind AI...")

    # Ensure backend path is on sys.path
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    if args.dev:
        print("[*] Mode: DEVELOPMENT (FastAPI + Vite Hot Reload)")
        print(f"[*] FastAPI API:   http://{args.host}:{args.port}")
        print(f"[*] React Frontend: http://localhost:5173")
        print(f"[*] Swagger Docs:  http://{args.host}:{args.port}/api/docs\n")

        # Launch uvicorn
        import uvicorn
        uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=True)
    else:
        print("[*] Mode: UNIFIED PRODUCTION (FastAPI + React SPA)")
        print(f"[*] Web Interface: http://{args.host}:{args.port}")
        print(f"[*] API Docs:      http://{args.host}:{args.port}/api/docs\n")

        import uvicorn
        uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
