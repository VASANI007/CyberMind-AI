"""
Project Paths
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
CONFIG_DIR = BASE_DIR / "config"
CORE_DIR = BASE_DIR / "core"
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
ML_DIR = BASE_DIR / "ml"
MODULES_DIR = BASE_DIR / "modules"
PAGES_DIR = BASE_DIR / "pages"
REPORTS_DIR = BASE_DIR / "reports"
SCHEMAS_DIR = BASE_DIR / "schemas"
SERVICES_DIR = BASE_DIR / "services"
TEMP_DIR = BASE_DIR / "temp"
TESTS_DIR = BASE_DIR / "tests"
UTILS_DIR = BASE_DIR / "utils"

DATABASE_PATH = DATABASE_DIR / "cybermind.db"

LOGO_DIR = ASSETS_DIR / "logo"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
CSS_DIR = ASSETS_DIR / "css"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"

MODEL_DIR = ML_DIR / "models"
DATASET_DIR = ML_DIR / "datasets"
TRAINING_DIR = ML_DIR / "training"
PREDICTION_DIR = ML_DIR / "prediction"
NOTEBOOKS_DIR = ML_DIR / "notebooks"