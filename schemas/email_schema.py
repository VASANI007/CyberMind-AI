"""
CyberMind AI

Email Schema

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


class EmailSchema(
    BaseSchema
):
    """
    Enterprise Email Schema.
    """

    scanner: str = "email"

    email: str = Field(

        default="",

        description="Email address."

    )

    username: str = Field(

        default="",

        description="Email username."

    )

    domain: str = Field(

        default="",

        description="Email domain."

    )

    disposable: bool = Field(

        default=False,

        description="Disposable email."

    )

    free_provider: bool = Field(

        default=False,

        description="Free email provider."

    )

    valid_format: bool = Field(

        default=False,

        description="Email format validation."

    )

    mx_records: list[str] = Field(

        default_factory=list

    )

    spf: dict[str, Any] = Field(

        default_factory=dict

    )

    dkim: dict[str, Any] = Field(

        default_factory=dict

    )

    dmarc: dict[str, Any] = Field(

        default_factory=dict

    )

    dns: dict[str, Any] = Field(

        default_factory=dict

    )

    reputation: dict[str, Any] = Field(

        default_factory=dict

    )

    blacklist: dict[str, Any] = Field(

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
        Email summary.
        """

        return {

            "success": self.success,

            "email": self.email,

            "domain": self.domain,

            "valid_format": self.valid_format,

            "disposable": self.disposable,

            "risk": self.risk,

            "reputation": self.reputation

        }

    def reset(
        self
    ) -> None:
        """
        Reset schema.
        """

        self.username = ""

        self.domain = ""

        self.disposable = False

        self.free_provider = False

        self.valid_format = False

        self.mx_records = []

        self.spf = {}

        self.dkim = {}

        self.dmarc = {}

        self.dns = {}

        self.reputation = {}

        self.blacklist = {}

        self.risk = {}

        self.recommendation = {}

        self.explain_ai = {}

        self.metadata = {}

    def __repr__(
        self
    ) -> str:

        return (

            "EmailSchema("

            "Enterprise Version)"

        )