"""
CyberMind AI

Report Schema

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


class ReportSchema(
    BaseSchema
):
    """
    Enterprise Report Schema.
    """

    scanner: str = "report"

    report_id: str = Field(

        default="",

        description="Unique report ID."

    )

    report_name: str = Field(

        default="",

        description="Report name."

    )

    report_type: str = Field(

        default="General",

        description="Report type."

    )

    generated_by: str = Field(

        default="CyberMind AI",

        description="Report generator."

    )

    generated_at: str = Field(

        default="",

        description="Generation timestamp."

    )

    total_scans: int = Field(

        default=0,

        description="Total scans."

    )

    success_count: int = Field(

        default=0,

        description="Successful scans."

    )

    failed_count: int = Field(

        default=0,

        description="Failed scans."

    )

    safe_count: int = Field(

        default=0,

        description="Safe results."

    )

    warning_count: int = Field(

        default=0,

        description="Warning results."

    )

    malicious_count: int = Field(

        default=0,

        description="Malicious results."

    )

    report_data: list[dict[str, Any]] = Field(

        default_factory=list

    )

    summary: dict[str, Any] = Field(

        default_factory=dict

    )

    charts: list[str] = Field(

        default_factory=list

    )

    exported_files: list[str] = Field(

        default_factory=list

    )

    metadata: dict[str, Any] = Field(

        default_factory=dict

    )

    def statistics(
        self
    ) -> dict[str, int]:
        """
        Report statistics.
        """

        return {

            "total_scans": self.total_scans,

            "success_count": self.success_count,

            "failed_count": self.failed_count,

            "safe_count": self.safe_count,

            "warning_count": self.warning_count,

            "malicious_count": self.malicious_count

        }

    def reset(
        self
    ) -> None:
        """
        Reset report.
        """

        self.report_id = ""

        self.report_name = ""

        self.report_type = "General"

        self.generated_by = "CyberMind AI"

        self.generated_at = ""

        self.total_scans = 0

        self.success_count = 0

        self.failed_count = 0

        self.safe_count = 0

        self.warning_count = 0

        self.malicious_count = 0

        self.report_data = []

        self.summary = {}

        self.charts = []

        self.exported_files = []

        self.metadata = {}

    def __repr__(
        self
    ) -> str:

        return (

            "ReportSchema("

            "Enterprise Version)"

        )