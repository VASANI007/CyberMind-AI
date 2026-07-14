"""
CyberMind AI

QR Schema

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


class QRSchema(
    BaseSchema
):
    """
    Enterprise QR Schema.
    """

    scanner: str = "qr"

    image_path: str = Field(

        default="",

        description="QR image path."

    )

    decoded_text: str = Field(

        default="",

        description="Decoded QR content."

    )

    content_type: str = Field(

        default="Unknown",

        description="QR content type."

    )

    is_valid_qr: bool = Field(

        default=False,

        description="QR validation status."

    )

    contains_url: bool = Field(

        default=False,

        description="Contains URL."

    )

    contains_email: bool = Field(

        default=False,

        description="Contains Email."

    )

    contains_phone: bool = Field(

        default=False,

        description="Contains Phone."

    )

    contains_wifi: bool = Field(

        default=False,

        description="Contains WiFi configuration."

    )

    contains_vcard: bool = Field(

        default=False,

        description="Contains Contact Card."

    )

    url_analysis: dict[str, Any] = Field(

        default_factory=dict

    )

    metadata: dict[str, Any] = Field(

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
        QR summary.
        """

        return {

            "success": self.success,

            "content_type": self.content_type,

            "decoded_text": self.decoded_text,

            "contains_url": self.contains_url,

            "risk": self.risk,

            "reputation": self.reputation

        }

    def reset(
        self
    ) -> None:
        """
        Reset schema.
        """

        self.image_path = ""

        self.decoded_text = ""

        self.content_type = "Unknown"

        self.is_valid_qr = False

        self.contains_url = False

        self.contains_email = False

        self.contains_phone = False

        self.contains_wifi = False

        self.contains_vcard = False

        self.url_analysis = {}

        self.metadata = {}

        self.reputation = {}

        self.risk = {}

        self.recommendation = {}

        self.explain_ai = {}

    def __repr__(
        self
    ) -> str:

        return (

            "QRSchema("

            "Enterprise Version)"

        )