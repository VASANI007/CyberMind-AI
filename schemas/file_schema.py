"""
CyberMind AI

File Schema

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


class FileSchema(
    BaseSchema
):
    """
    Enterprise File Schema.
    """

    scanner: str = "file"

    filename: str = Field(

        default="",

        description="File name."

    )

    file_path: str = Field(

        default="",

        description="Absolute file path."

    )

    extension: str = Field(

        default="",

        description="File extension."

    )

    mime_type: str = Field(

        default="",

        description="MIME type."

    )

    size: int = Field(

        default=0,

        description="File size in bytes."

    )

    md5: str = Field(

        default="",

        description="MD5 hash."

    )

    sha1: str = Field(

        default="",

        description="SHA1 hash."

    )

    sha256: str = Field(

        default="",

        description="SHA256 hash."

    )

    entropy: float = Field(

        default=0.0,

        description="File entropy."

    )

    malicious: bool = Field(

        default=False,

        description="Malicious detection."

    )

    file_type: str = Field(

        default="",

        description="Detected file type."

    )

    metadata: dict[str, Any] = Field(

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
        File summary.
        """

        return {

            "success": self.success,

            "filename": self.filename,

            "extension": self.extension,

            "size": self.size,

            "malicious": self.malicious,

            "risk": self.risk,

            "reputation": self.reputation

        }

    def reset(
        self
    ) -> None:
        """
        Reset schema.
        """

        self.filename = ""

        self.file_path = ""

        self.extension = ""

        self.mime_type = ""

        self.size = 0

        self.md5 = ""

        self.sha1 = ""

        self.sha256 = ""

        self.entropy = 0.0

        self.malicious = False

        self.file_type = ""

        self.metadata = {}

        self.virustotal = {}

        self.reputation = {}

        self.risk = {}

        self.recommendation = {}

        self.explain_ai = {}

    def __repr__(
        self
    ) -> str:

        return (

            "FileSchema("

            "Enterprise Version)"

        )