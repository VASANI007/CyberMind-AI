"""
CyberMind AI

Domain Schema

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


class DomainSchema(
    BaseSchema
):
    """
    Enterprise Domain Schema.
    """

    scanner: str = "domain"

    domain: str = Field(

        default="",

        description="Domain name."

    )

    hostname: str = Field(

        default="",

        description="Hostname."

    )

    registrar: str = Field(

        default="",

        description="Domain registrar."

    )

    creation_date: str = Field(

        default="",

        description="Domain creation date."

    )

    expiration_date: str = Field(

        default="",

        description="Domain expiration date."

    )

    updated_date: str = Field(

        default="",

        description="Last update date."

    )

    age_days: int = Field(

        default=0,

        description="Domain age."

    )

    nameservers: list[str] = Field(

        default_factory=list

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

    blacklist: dict[str, Any] = Field(

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

    metadata: dict[str, Any] = Field(

        default_factory=dict

    )

    def summary(
        self
    ) -> dict[str, Any]:
        """
        Domain summary.
        """

        return {

            "success": self.success,

            "domain": self.domain,

            "registrar": self.registrar,

            "age_days": self.age_days,

            "risk": self.risk,

            "reputation": self.reputation

        }

    def reset(
        self
    ) -> None:
        """
        Reset schema.
        """

        self.hostname = ""

        self.registrar = ""

        self.creation_date = ""

        self.expiration_date = ""

        self.updated_date = ""

        self.age_days = 0

        self.nameservers = []

        self.dns = {}

        self.whois = {}

        self.ssl = {}

        self.blacklist = {}

        self.reputation = {}

        self.risk = {}

        self.recommendation = {}

        self.explain_ai = {}

        self.metadata = {}

    def __repr__(
        self
    ) -> str:

        return (

            "DomainSchema("

            "Enterprise Version)"

        )