"""
CyberMind AI

Base Schema

Enterprise Production Version
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class BaseSchema(
    BaseModel
):
    """
    Enterprise Base Schema.

    Parent schema for all
    CyberMind AI schemas.
    """

    model_config = ConfigDict(

        validate_assignment=True,

        extra="ignore",

        frozen=False,

        populate_by_name=True

    )

    success: bool = Field(

        default=True,

        description="Operation status."

    )

    message: str = Field(

        default="Success",

        description="Status message."

    )

    scanner: str = Field(

        default="",

        description="Scanner name."

    )

    version: str = Field(

        default="2.0.0",

        description="Schema version."

    )

    timestamp: datetime = Field(

        default_factory=datetime.utcnow,

        description="Creation timestamp."

    )

    metadata: dict[str, Any] = Field(

        default_factory=dict,

        description="Additional metadata."

    )

    def to_dict(
        self
    ) -> dict[str, Any]:
        """
        Export dictionary.
        """

        return self.model_dump()

    def to_json(
        self,
        indent: int = 4
    ) -> str:
        """
        Export JSON.
        """

        return self.model_dump_json(

            indent=indent

        )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any]
    ) -> "BaseSchema":
        """
        Create schema from dictionary.
        """

        return cls(

            **data

        )

    @classmethod
    def from_json(
        cls,
        data: str
    ) -> "BaseSchema":
        """
        Create schema from JSON.
        """

        return cls.model_validate_json(

            data

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Schema health.
        """

        return {

            "schema":

                self.__class__.__name__,

            "status":

                "Healthy",

            "version":

                self.version

        }

    def __repr__(
        self
    ) -> str:

        return (

            f"{self.__class__.__name__}"

            "(Enterprise Version)"

        )