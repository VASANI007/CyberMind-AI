"""
CyberMind AI

Dashboard Engine

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger

from modules.analytics_engine import (
    analytics_engine
)

from modules.risk_engine import (
    risk_engine
)


class DashboardEngine:
    """
    Enterprise Dashboard Engine.

    Responsibilities

    • Dashboard Summary

    • Statistics

    • Analytics

    • Charts Data

    • Recent Activity

    • Risk Summary
    """

    VERSION = "2.0.0"

    def __init__(
        self
    ) -> None:

        logger.info(

            "Dashboard Engine initialized."

        )

    def summary(
        self
    ) -> dict[str, Any]:
        """
        Dashboard summary.
        """

        dashboard = analytics_engine.dashboard()

        return {

            "application":

                "CyberMind AI",

            "version":

                self.VERSION,

            "total_scans":

                dashboard.get(

                    "total_scans",

                    0

                ),

            "success_rate":

                dashboard.get(

                    "success_rate",

                    0.0

                ),

            "scanner_usage":

                dashboard.get(

                    "scanner_usage",

                    {}

                ),

            "risk_distribution":

                dashboard.get(

                    "risk_distribution",

                    {}

                )

        }

    def analytics(
        self
    ) -> dict[str, Any]:
        """
        Analytics data.
        """

        return analytics_engine.dashboard()

    def recent_activity(
        self,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Recent scan activity.
        """

        history = analytics_engine.history

        return history[-limit:]

    def risk_summary(
        self
    ) -> dict[str, Any]:
        """
        Risk summary.
        """

        distribution = (

            analytics_engine.risk_distribution()

        )

        return {

            "levels":

                distribution,

            "supported_levels":

                risk_engine.supported_levels()

        }

    def statistics(
        self
    ) -> dict[str, Any]:
        """
        Dashboard statistics.
        """

        return {

            "history":

                analytics_engine.total_scans(),

            "scanner_usage":

                analytics_engine.scanner_statistics(),

            "risk_distribution":

                analytics_engine.risk_distribution(),

            "success_rate":

                analytics_engine.success_rate()

        }

    def refresh(
        self
    ) -> dict[str, Any]:
        """
        Refresh dashboard.
        """

        logger.info(

            "Dashboard refreshed."

        )

        return self.summary()

    def clear(
        self
    ) -> None:
        """
        Clear dashboard analytics.
        """

        analytics_engine.clear()

        logger.info(

            "Dashboard cleared."

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Dashboard health.
        """

        return {

            "service":

                "Dashboard Engine",

            "status":

                "Healthy",

            "version":

                self.VERSION

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "Dashboard Summary",

            "Analytics",

            "Recent Activity",

            "Risk Summary",

            "Statistics",

            "Refresh Dashboard",

            "Health Check"

        ]

    def __repr__(
        self
    ) -> str:

        return (

            "DashboardEngine("

            "Enterprise Version)"

        )


dashboard_engine = DashboardEngine()