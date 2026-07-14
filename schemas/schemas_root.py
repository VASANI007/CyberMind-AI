"""
CyberMind AI
Schemas Root Manager
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

from schemas.base_schema import BaseSchema
from schemas.url_schema import URLSchema
from schemas.website_schema import WebsiteSchema
from schemas.domain_schema import DomainSchema
from schemas.email_schema import EmailSchema
from schemas.ip_schema import IPSchema
from schemas.file_schema import FileSchema
from schemas.qr_schema import QRSchema
from schemas.report_schema import ReportSchema
from schemas.dashboard_schema import DashboardSchema


class SchemasRoot:
    """
    Schemas Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:
        self.schemas = {
            "BaseSchema": BaseSchema,
            "URLSchema": URLSchema,
            "WebsiteSchema": WebsiteSchema,
            "DomainSchema": DomainSchema,
            "EmailSchema": EmailSchema,
            "IPSchema": IPSchema,
            "FileSchema": FileSchema,
            "QRSchema": QRSchema,
            "ReportSchema": ReportSchema,
            "DashboardSchema": DashboardSchema
        }

    def initialize(self) -> None:
        """
        Initialize schemas layer.
        """
        logger.info("Initializing Schemas...")
        for name in self.schemas.keys():
            logger.info(f"Schema {name} loaded.")

    def health_check(self) -> dict[str, Any]:
        """
        Schemas health check.
        """
        results = {}
        healthy = True
        for name, schema_cls in self.schemas.items():
            try:
                # Instantiate and check health
                instance = schema_cls()
                status = instance.health_check() if hasattr(instance, "health_check") else {"status": "Healthy"}
                results[name] = status
                if status.get("status") != "Healthy":
                    healthy = False
            except Exception as e:
                healthy = False
                results[name] = {"status": "Unhealthy", "error": str(e)}

        return {
            "service": "Schemas",
            "status": "Healthy" if healthy else "Unhealthy",
            "schemas": results
        }

    def status(self) -> dict[str, Any]:
        """
        Schemas status.
        """
        return {
            "version": self.VERSION,
            "total_schemas": len(self.schemas),
            "health": self.health_check()
        }

    def reload(self) -> None:
        """
        Reload schemas.
        """
        logger.info("Reloading Schemas...")
        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown schemas.
        """
        logger.info("Schemas manager shutdown.")

    def list_schemas(self) -> list[str]:
        """
        List all schemas.
        """
        return sorted(list(self.schemas.keys()))

    def __len__(self) -> int:
        return len(self.schemas)

    def __repr__(self) -> str:
        return (
            f"SchemasRoot("
            f"schemas={len(self.schemas)}, "
            f"version='{self.VERSION}')"
        )


schemas_root = SchemasRoot()

if __name__ == "__main__":
    # Configure stdout and stderr to support UTF-8 characters (emojis) on Windows terminals
    if sys.platform.startswith('win'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("=" * 60)
    print("             🛡️  CyberMind AI - Schemas Runner 🛡️             ")
    print("=" * 60)
    schemas_root.initialize()
    health = schemas_root.health_check()
    print(f"Status: {health['status']}")
    for name, stat in health["schemas"].items():
        print(f"  - {name}: {stat.get('status')}")
    print("=" * 60)
