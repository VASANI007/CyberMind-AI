"""
CyberMind AI
Utilities Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import io
import pathlib
import sys

# Add project root to path for direct execution support
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from typing import Any
from core.logger import logger

from utils.chart_utils import chart_utils
from utils.date_utils import date_utils
from utils.file_utils import file_utils
from utils.hash_utils import hash_utils
from utils.network_utils import network_utils
from utils.report_utils import report_utils
from utils.string_utils import string_utils


class UtilRoot:
    """
    Utilities Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:
        self.utilities = {
            "chart_utils": chart_utils,
            "date_utils": date_utils,
            "file_utils": file_utils,
            "hash_utils": hash_utils,
            "network_utils": network_utils,
            "report_utils": report_utils,
            "string_utils": string_utils
        }

    def initialize(self) -> None:
        """
        Initialize utilities.
        """
        logger.info("Initializing Utilities...")
        for name in self.utilities.keys():
            logger.info(f"Utility {name} loaded.")

    def health_check(self) -> dict[str, Any]:
        """
        Utilities health check.
        """
        results = {}
        healthy = True
        for name, util in self.utilities.items():
            try:
                status = util.health_check() if hasattr(util, "health_check") else {"status": "Healthy"}
                results[name] = status
                if status.get("status") != "Healthy":
                    healthy = False
            except Exception as e:
                healthy = False
                results[name] = {"status": "Unhealthy", "error": str(e)}

        return {
            "service": "Utilities",
            "status": "Healthy" if healthy else "Unhealthy",
            "utilities": results
        }

    def status(self) -> dict[str, Any]:
        """
        Utilities status.
        """
        return {
            "version": self.VERSION,
            "total_utilities": len(self.utilities),
            "health": self.health_check()
        }

    def reload(self) -> None:
        """
        Reload utilities.
        """
        logger.info("Reloading Utilities...")
        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown utilities.
        """
        logger.info("Utilities manager shutdown.")

    def list_utilities(self) -> list[str]:
        """
        List all utilities.
        """
        return sorted(list(self.utilities.keys()))

    def __len__(self) -> int:
        return len(self.utilities)

    def __repr__(self) -> str:
        return (
            f"UtilRoot("
            f"utilities={len(self.utilities)}, "
            f"version='{self.VERSION}')"
        )


util_root = UtilRoot()

if __name__ == "__main__":
    # Configure stdout and stderr to support UTF-8 characters (emojis) on Windows terminals
    if sys.platform.startswith('win'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("=" * 60)
    print("             🛡️  CyberMind AI - Utilities Runner 🛡️             ")
    print("=" * 60)
    util_root.initialize()
    health = util_root.health_check()
    print(f"Status: {health['status']}")
    for name, stat in health["utilities"].items():
        print(f"  - {name}: {stat.get('status')}")
    print("=" * 60)
