"""
CyberMind AI

URL Schema

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


class URLSchema(
    BaseSchema
):
    """
    Enterprise URL Schema.
    """

    scanner: str = "url"

    url: str = Field(

        default="",

        description="Input URL."

    )

    hostname: str = Field(

        default="",

        description="Hostname."

    )

    metadata: dict[str, Any] = Field(

        default_factory=dict

    )

    features: dict[str, Any] = Field(

        default_factory=dict

    )

    dns: dict[str, Any] = Field(

        default_factory=dict

    )

    whois: dict[str, Any] = Field(

        default_factory=dict

    )

    ssl: dict[str, Any] = Field(

        default_factory=dict

    )

    security_headers: dict[str, Any] = Field(

        default_factory=dict

    )

    blacklist: dict[str, Any] = Field(

        default_factory=dict

    )

    google_safe_browsing: dict[str, Any] = Field(

        default_factory=dict

    )

    virustotal: dict[str, Any] = Field(

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
        Short summary.
        """

        return {

            "success": self.success,

            "url": self.url,

            "hostname": self.hostname,

            "risk": self.risk,

            "reputation": self.reputation

        }

    def reset(
        self
    ) -> None:
        """
        Reset schema.
        """

        self.metadata = {}

        self.features = {}

        self.dns = {}

        self.whois = {}

        self.ssl = {}

        self.security_headers = {}

        self.blacklist = {}

        self.google_safe_browsing = {}

        self.virustotal = {}

        self.reputation = {}

        self.risk = {}

        self.recommendation = {}

        self.explain_ai = {}

    def __repr__(
        self
    ) -> str:

        return (

            "URLSchema("

            "Enterprise Version)"

        )