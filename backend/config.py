"""
CyberMind AI - Backend Configuration
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env", override=True)

APP_NAME = os.getenv("APP_NAME", "CyberMind AI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5173"))

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Additional allowed origins from environment
EXTRA_ORIGINS = os.getenv("CORS_ORIGINS", "")
if EXTRA_ORIGINS:
    for origin in EXTRA_ORIGINS.split(","):
        origin_clean = origin.strip()
        if origin_clean and origin_clean not in CORS_ORIGINS:
            CORS_ORIGINS.append(origin_clean)

DATABASE_PATH = BASE_DIR / "database" / "cybermind.db"
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = BASE_DIR / "reports" / "generated"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
