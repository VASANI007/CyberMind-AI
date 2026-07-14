"""
===========================================================
CyberMind AI
Application Settings
===========================================================
"""

import os
from pathlib import Path

from config.env import *

# ==========================================================
# Project Information
# ==========================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "CyberMind AI"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

APP_AUTHOR = os.getenv(
    "REPORT_AUTHOR",
    "Daksh Vasani"
)

APP_DESCRIPTION = (
    "AI-Powered Cyber Risk Assessment & Threat Intelligence Platform"
)

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# Application Settings
# ==========================================================

DEBUG = os.getenv(
    "DEBUG",
    "True"
) == "True"

APP_ICON = "🛡️"

PAGE_LAYOUT = "wide"

SIDEBAR_STATE = "expanded"

# ==========================================================
# Database
# ==========================================================

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "cybermind.db"
)

DATABASE_PATH = BASE_DIR / "database" / DATABASE_NAME

# ==========================================================
# Export Folder
# ==========================================================

EXPORT_PATH = BASE_DIR / "exports"

# ==========================================================
# Logs
# ==========================================================

LOG_PATH = BASE_DIR / "logs"

# ==========================================================
# Assets
# ==========================================================

ASSETS_PATH = BASE_DIR / "assets"

LOGO_PATH = ASSETS_PATH / "logo"

IMAGE_PATH = ASSETS_PATH / "images"

ICON_PATH = ASSETS_PATH / "icons"

CSS_PATH = ASSETS_PATH / "css"

# ==========================================================
# Machine Learning
# ==========================================================

MODEL_PATH = BASE_DIR / "ml" / "models"

DATASET_PATH = BASE_DIR / "data"

# ==========================================================
# Reports
# ==========================================================

REPORT_TITLE = "CyberMind AI Security Report"

REPORT_AUTHOR = os.getenv(
    "REPORT_AUTHOR",
    APP_AUTHOR
)

REPORT_COMPANY = os.getenv(
    "REPORT_COMPANY",
    "CyberMind AI"
)


class Settings:
    @property
    def PROJECT_NAME(self) -> str:
        return APP_NAME

    @property
    def VERSION(self) -> str:
        return APP_VERSION

    @property
    def DEBUG(self) -> bool:
        return DEBUG

    @property
    def LOG_DIR(self) -> Path:
        return LOG_PATH

    @property
    def DATABASE_PATH(self) -> Path:
        return DATABASE_PATH

    @property
    def MODEL_DIR(self) -> Path:
        return MODEL_PATH

    @property
    def REPORT_DIR(self) -> Path:
        return EXPORT_PATH


settings = Settings()