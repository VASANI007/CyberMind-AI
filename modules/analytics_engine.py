"""
CyberMind AI

Analytics Engine

Enterprise Production Version
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from core.logger import logger


class AnalyticsEngine:
    """
    Enterprise Analytics Engine.

    Responsibilities

    • Scan History

    • Statistics

    • Threat Distribution

    • Scanner Usage

    • Dashboard Data

    • Reports
    """

    def __init__(
        self
    ) -> None:

        self.history = []

        logger.info(

            "Analytics Engine initialized."

        )

    def add(
        self,
        report: dict[str, Any]
    ) -> None:
        """
        Add scan report.
        """

        report = report.copy()

        report["timestamp"] = (

            datetime.utcnow()

            .isoformat()

        )

        self.history.append(

            report

        )

    def total_scans(
        self
    ) -> int:
        """
        Total scans.
        """

        return len(

            self.history

        )

    def scanner_statistics(
        self
    ) -> dict[str, int]:
        """
        Scanner usage statistics.
        """

        counter = Counter()

        for item in self.history:

            counter.update(

                [

                    item.get(

                        "scanner",

                        "unknown"

                    )

                ]

            )

        return dict(

            counter

        )

    def risk_distribution(
        self
    ) -> dict[str, int]:
        """
        Risk level distribution.
        """

        counter = Counter()

        for item in self.history:

            level = (

                item.get(

                    "risk",

                    {}

                )

                .get(

                    "level",

                    "Unknown"

                )

            )

            counter.update(

                [

                    level

                ]

            )

        return dict(

            counter

        )

    def success_rate(
        self
    ) -> float:
        """
        Scan success percentage.
        """

        if not self.history:

            return 0.0

        success = sum(

            item.get(

                "success",

                False

            )

            for item

            in self.history

        )

        return round(

            (

                success

                /

                len(

                    self.history

                )

            )

            *

            100,

            2

        )

    def dashboard(
        self
    ) -> dict[str, Any]:
        """
        Dashboard summary.
        """

        return {

            "total_scans":

                self.total_scans(),

            "success_rate":

                self.success_rate(),

            "scanner_usage":

                self.scanner_statistics(),

            "risk_distribution":

                self.risk_distribution()

        }

    def clear(
        self
    ) -> None:
        """
        Clear analytics history.
        """

        self.history.clear()

        logger.info(

            "Analytics history cleared."

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Engine health.
        """

        return {

            "service":

                "Analytics Engine",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "Scan History",

            "Dashboard",

            "Statistics",

            "Risk Distribution",

            "Success Rate",

            "Reports"

        ]

    def __repr__(
        self
    ) -> str:

        return (

            "AnalyticsEngine("

            "Enterprise Version)"

        )


analytics_engine = AnalyticsEngine()