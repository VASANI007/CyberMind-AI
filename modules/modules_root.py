"""
CyberMind AI
Modules Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from typing import Any

from core.logger import logger

from modules.scanner_engine import scanner_engine
from modules.analytics_engine import analytics_engine
from modules.dashboard_engine import dashboard_engine
from modules.risk_engine import risk_engine
from modules.recommendation import recommendation_engine
from modules.explain_ai import explain_ai

from modules.url_scanner import url_scanner
from modules.website_scanner import website_scanner
from modules.domain_scanner import domain_scanner
from modules.email_scanner import email_scanner
from modules.ip_scanner import ip_scanner
from modules.file_scanner import file_scanner
from modules.qr_scanner import qr_scanner


class ModulesRoot:
    """
    Enterprise Modules Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.engines = {

            "Scanner Engine": scanner_engine,

            "Analytics Engine": analytics_engine,

            "Dashboard Engine": dashboard_engine,

            "Risk Engine": risk_engine,

            "Recommendation Engine": recommendation_engine,

            "Explain AI": explain_ai

        }

        self.scanners = {

            "URL": url_scanner,

            "Website": website_scanner,

            "Domain": domain_scanner,

            "Email": email_scanner,

            "IP": ip_scanner,

            "File": file_scanner,

            "QR": qr_scanner

        }

        logger.info(
            "Modules Root Initialized."
        )

    def initialize(self) -> None:
        """
        Initialize modules.
        """

        logger.info(
            "Initializing Modules..."
        )

        self.initialize_engines()

        self.initialize_scanners()

        logger.info(
            "Modules Ready."
        )

    def initialize_engines(self) -> None:
        """
        Initialize engines.
        """

        logger.info(
            "Loading Engines..."
        )

        for name in self.engines:

            logger.info(
                "%s Loaded.",
                name
            )

    def initialize_scanners(self) -> None:
        """
        Initialize scanners.
        """

        logger.info(
            "Loading Scanners..."
        )

        for name in self.scanners:

            logger.info(
                "%s Scanner Ready.",
                name
            )

    def engine_count(self) -> int:
        """
        Total engines.
        """

        return len(
            self.engines
        )

    def scanner_count(self) -> int:
        """
        Total scanners.
        """

        return len(
            self.scanners
        )

    def list_engines(self) -> list[str]:
        """
        List engines.
        """

        return sorted(
            self.engines.keys()
        )

    def list_scanners(self) -> list[str]:
        """
        List scanners.
        """

        return sorted(
            self.scanners.keys()
        )
        
        
        
    def health_check(self) -> dict[str, Any]:
        """
        Modules health.
        """

        engines = {

            name:

            engine.health_check()

            for name, engine

            in self.engines.items()

        }

        scanners = {

            name:

            scanner.health_check()

            for name, scanner

            in self.scanners.items()

        }

        healthy = all(

            item["status"] == "Healthy"

            for item

            in list(

                engines.values()

            )

            +

            list(

                scanners.values()

            )

        )

        return {

            "service":
                "Modules",

            "status":
                "Healthy"
                if healthy
                else "Unhealthy",

            "engines":
                engines,

            "scanners":
                scanners

        }

    def statistics(self) -> dict[str, Any]:
        """
        Modules statistics.
        """

        return {

            "engines":
                self.engine_count(),

            "scanners":
                self.scanner_count(),

            "registered_scanners":
                scanner_engine.registered_scanners(),

            "scan_statistics":
                scanner_engine.statistics_report(),

            "total_scans":
                scanner_engine.total_scans()

        }

    def dashboard(self) -> dict[str, Any]:
        """
        Dashboard summary.
        """

        return dashboard_engine.summary()

    def analytics(self) -> dict[str, Any]:
        """
        Analytics summary.
        """

        return analytics_engine.dashboard()

    def status(self) -> dict[str, Any]:
        """
        Modules status.
        """

        return {

            "version":
                self.VERSION,

            "health":
                self.health_check(),

            "statistics":
                self.statistics(),

            "dashboard":
                self.dashboard()

        }

    def clear_analytics(self) -> None:
        """
        Clear analytics.
        """

        analytics_engine.clear()

        scanner_engine.clear_history()

        scanner_engine.reset_statistics()

        logger.info(
            "Modules analytics cleared."
        )

    def reload(self) -> None:
        """
        Reload modules.
        """

        logger.info(
            "Reloading Modules..."
        )

        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown modules.
        """

        logger.info(
            "Modules shutdown completed."
        )

    def __len__(self) -> int:
        """
        Total scanners.
        """

        return self.scanner_count()

    def __repr__(self) -> str:
        """
        String representation.
        """

        return (

            f"ModulesRoot("
            f"engines={self.engine_count()}, "
            f"scanners={self.scanner_count()}, "
            f"version='{self.VERSION}')"

        )


modules_root = ModulesRoot()