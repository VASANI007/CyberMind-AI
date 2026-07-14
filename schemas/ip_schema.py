"""
CyberMind AI

IP Schema

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


class IPSchema(
    BaseSchema
):
    """
    Enterprise IP Schema.
    """

    scanner: str = "ip"

    ip: str = Field(

        default="",

        description="IP address."

    )

    version: str = Field(

        default="IPv4",

        description="IP version."

    )

    hostname: str = Field(

        default="",

        description="Reverse hostname."

    )

    isp: str = Field(

        default="",

        description="Internet Service Provider."

    )

    organization: str = Field(

        default="",

        description="Organization."

    )

    asn: str = Field(

        default="",

        description="Autonomous System Number."

    )

    country: str = Field(

        default="",

        description="Country."

    )

    region: str = Field(

        default="",

        description="Region."

    )

    city: str = Field(

        default="",

        description="City."

    )

    latitude: float = Field(

        default=0.0,

        description="Latitude."

    )

    longitude: float = Field(

        default=0.0,

        description="Longitude."

    )

    timezone: str = Field(

        default="",

        description="Timezone."

    )

    geo: dict[str, Any] = Field(

        default_factory=dict

    )

    abuseipdb: dict[str, Any] = Field(

        default_factory=dict

    )

    ipinfo: dict[str, Any] = Field(

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
        IP summary.
        """

        return {

            "success": self.success,

            "ip": self.ip,

            "country": self.country,

            "city": self.city,

            "isp": self.isp,

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

        self.isp = ""

        self.organization = ""

        self.asn = ""

        self.country = ""

        self.region = ""

        self.city = ""

        self.latitude = 0.0

        self.longitude = 0.0

        self.timezone = ""

        self.geo = {}

        self.abuseipdb = {}

        self.ipinfo = {}

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

            "IPSchema("

            "Enterprise Version)"

        )