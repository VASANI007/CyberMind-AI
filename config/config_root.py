"""
CyberMind AI
Configuration Root Manager
Enterprise Production Version
"""

from __future__ import annotations
import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from pathlib import Path
from typing import Any

from core.logger import logger

from config.settings import settings
from config.constants import Constants
from config.paths import *
from config.theme import *
from config.menu import MENU_ITEMS
from config.api_config import *
from config.env import *


class ConfigRoot:
    """
    Configuration Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.settings = settings

        self.constants = Constants

        self.menu = MENU_ITEMS

    def initialize(self) -> None:
        """
        Initialize configuration.
        """

        logger.info(
            "Initializing configuration..."
        )

        required_paths = [
            BASE_DIR,
            CONFIG_DIR,
            DATA_DIR,
            DATABASE_DIR,
            ML_DIR,
            REPORTS_DIR,
            LOGS_DIR,
            TEMP_DIR
        ]
        for path in required_paths:
            Path(path).mkdir(parents=True, exist_ok=True)

        logger.info(
            "Application : %s",
            settings.PROJECT_NAME
        )

        logger.info(
            "Version : %s",
            settings.VERSION
        )

        logger.info(
            "Debug : %s",
            settings.DEBUG
        )

        logger.info(
            "Configuration initialized."
        )

    def health_check(self) -> dict[str, Any]:
        """
        Configuration health.
        """

        healthy = True

        required_paths = [

            BASE_DIR,

            CONFIG_DIR,

            DATA_DIR,

            DATABASE_DIR,

            ML_DIR,

            REPORTS_DIR,

            LOGS_DIR,

            TEMP_DIR

        ]

        missing = []

        for path in required_paths:

            if not Path(path).exists():

                healthy = False

                missing.append(
                    str(path)
                )

        return {

            "service": "Configuration",

            "status": (
                "Healthy"
                if healthy
                else "Unhealthy"
            ),

            "missing_paths": missing

        }

    def status(self) -> dict[str, Any]:
        """
        Configuration status.
        """

        return {

            "application": settings.PROJECT_NAME,

            "version": settings.VERSION,

            "debug": settings.DEBUG,

            "theme": PAGE_TITLE,

            "menu_items": len(
                self.menu
            )

        }

    def reload(self) -> None:
        """
        Reload configuration.
        """

        logger.info(
            "Reloading configuration..."
        )

        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown configuration.
        """

        logger.info(
            "Configuration shutdown."
        )

    def list_paths(self) -> dict[str, Path]:
        """
        Project paths.
        """

        return {

            "BASE_DIR": BASE_DIR,

            "CONFIG_DIR": CONFIG_DIR,

            "DATABASE_DIR": DATABASE_DIR,

            "DATA_DIR": DATA_DIR,

            "ML_DIR": ML_DIR,

            "REPORTS_DIR": REPORTS_DIR,

            "LOGS_DIR": LOGS_DIR,

            "TEMP_DIR": TEMP_DIR

        }

    def list_menu(self) -> list[dict]:
        """
        Sidebar menu.
        """

        return self.menu

    def __len__(self) -> int:

        return len(
            self.menu
        )

    def __repr__(self) -> str:

        return (

            f"ConfigRoot("
            f"version='{self.VERSION}', "
            f"menus={len(self.menu)})"

        )


config_root = ConfigRoot()