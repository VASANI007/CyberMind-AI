"""
CyberMind AI

Website Schema

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


class WebsiteSchema(
    BaseSchema
):
    """
    Enterprise Website Schema.
    """

    scanner: str = "website"

    url: str = Field(

        default="",

        description="Website URL."

    )

    title: str = Field(

        default="",

        description="Website title."

    )

    status_code: int = Field(

        default=0,

        description="HTTP status code."

    )

    response_time: float = Field(

        default=0.0,

        description="Response time."

    )

    ip_address: str = Field(

        default="",

        description="Resolved IP."

    )

    server: str = Field(

        default="",

        description="Web server."

    )

    technologies: list[str] = Field(

        default_factory=list

    )

    metadata: dict[str, Any] = Field(

        default_factory=dict

    )

    headers: dict[str, Any] = Field(

        default_factory=dict

    )

    ssl: dict[str, Any] = Field(

        default_factory=dict

    )

    dns: dict[str, Any] = Field(

        default_factory=dict

    )

    reputation: dict[str, Any] = Field(

        default_factory=dict

    )

    risk: dict[str, Any] = Field(

        default_factory=dict

    )

    recommendation: dict[str, Any] = Field(

        default_factory=dict

    )

    explain_ai: dict[str, Any] = Field(

        default_factory=dict

    )

    def summary(
        self
    ) -> dict[str, Any]:
        """
        Website summary.
        """

        return {

            "success": self.success,

            "url": self.url,

            "title": self.title,

            "status_code": self.status_code,

            "response_time": self.response_time,

            "risk": self.risk

        }

    def reset(
        self
    ) -> None:
        """
        Reset schema.
        """

        self.title = ""

        self.status_code = 0

        self.response_time = 0.0

        self.ip_address = ""

        self.server = ""

        self.technologies = []

        self.metadata = {}

        self.headers = {}

        self.ssl = {}

        self.dns = {}

        self.reputation = {}

        self.risk = {}

        self.recommendation = {}

        self.explain_ai = {}

    def __repr__(
        self
    ) -> str:

        return (

            "WebsiteSchema("

            "Enterprise Version)"

        )