"""
CyberMind AI

Dashboard Schema

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from pydantic import (
    Field
)

from schemas.base_schema import (
    BaseSchema
)


class DashboardSchema(
    BaseSchema
):
    """
    Enterprise Dashboard Schema.
    """

    scanner: str = "dashboard"

    application: str = Field(

        default="CyberMind AI",

        description="Application name."

    )

    version: str = Field(

        default="2.0.0",

        description="Application version."

    )

    total_scans: int = Field(

        default=0,

        description="Total scans."

    )

    successful_scans: int = Field(

        default=0,

        description="Successful scans."

    )

    failed_scans: int = Field(

        default=0,

        description="Failed scans."

    )

    scanner_usage: dict[str, int] = Field(

        default_factory=dict

    )

    risk_distribution: dict[str, int] = Field(

        default_factory=dict

    )

    recent_activity: list[dict[str, Any]] = Field(

        default_factory=list

    )

    charts: dict[str, Any] = Field(

        default_factory=dict

    )

    system_health: dict[str, Any] = Field(

        default_factory=dict

    )

    statistics: dict[str, Any] = Field(

        default_factory=dict

    )

    metadata: dict[str, Any] = Field(

        default_factory=dict

    )

    def summary(
        self
    ) -> dict[str, Any]:
        """
        Dashboard summary.
        """

        return {

            "application":

                self.application,

            "version":

                self.version,

            "total_scans":

                self.total_scans,

            "successful_scans":

                self.successful_scans,

            "failed_scans":

                self.failed_scans

        }

    @property
    def success_rate(
        self
    ) -> float:
        """
        Success percentage.
        """

        if self.total_scans == 0:

            return 0.0

        return round(

            (

                self.successful_scans

                /

                self.total_scans

            )

            * 100,

            2

        )

    @property
    def failure_rate(
        self
    ) -> float:
        """
        Failure percentage.
        """

        if self.total_scans == 0:

            return 0.0

        return round(

            (

                self.failed_scans

                /

                self.total_scans

            )

            * 100,

            2

        )

    def reset(
        self
    ) -> None:
        """
        Reset dashboard.
        """

        self.total_scans = 0

        self.successful_scans = 0

        self.failed_scans = 0

        self.scanner_usage = {}

        self.risk_distribution = {}

        self.recent_activity = []

        self.charts = {}

        self.system_health = {}

        self.statistics = {}

        self.metadata = {}

    def __repr__(
        self
    ) -> str:

        return (

            "DashboardSchema("

            "Enterprise Version)"

        )