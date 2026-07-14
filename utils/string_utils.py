"""
CyberMind AI

String Utilities

Enterprise Production Version
"""

from __future__ import annotations

import re
import unicodedata

from typing import Any

from core.logger import logger


class StringUtils:
    """
    Enterprise String Utility.

    Responsibilities

    • Clean Text

    • Normalize Text

    • Case Conversion

    • Validation

    • Tokenization

    • Slug Generation

    • Safe Filename
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "String Utils initialized."

        )

    def clean(
        self,
        text: str
    ) -> str:
        """
        Remove extra spaces.
        """

        return re.sub(

            r"\s+",

            " ",

            text

        ).strip()

    def normalize(
        self,
        text: str
    ) -> str:
        """
        Unicode normalize.
        """

        return unicodedata.normalize(

            "NFKC",

            text

        )

    def lowercase(
        self,
        text: str
    ) -> str:

        return text.lower()

    def uppercase(
        self,
        text: str
    ) -> str:

        return text.upper()

    def title(
        self,
        text: str
    ) -> str:

        return text.title()

    def capitalize(
        self,
        text: str
    ) -> str:

        return text.capitalize()

    def remove_special_characters(
        self,
        text: str
    ) -> str:
        """
        Remove special characters.
        """

        return re.sub(

            r"[^A-Za-z0-9 ]",

            "",

            text

        )

    def remove_digits(
        self,
        text: str
    ) -> str:
        """
        Remove digits.
        """

        return re.sub(

            r"\d",

            "",

            text

        )

    def only_digits(
        self,
        text: str
    ) -> str:
        """
        Keep only digits.
        """

        return re.sub(

            r"\D",

            "",

            text

        )

    def only_letters(
        self,
        text: str
    ) -> str:
        """
        Keep only letters.
        """

        return re.sub(

            r"[^A-Za-z]",

            "",

            text

        )

    def tokenize(
        self,
        text: str
    ) -> list[str]:
        """
        Split text into words.
        """

        return self.clean(

            text

        ).split()

    def word_count(
        self,
        text: str
    ) -> int:
        """
        Number of words.
        """

        return len(

            self.tokenize(

                text

            )

        )

    def character_count(
        self,
        text: str
    ) -> int:
        """
        Character count.
        """

        return len(

            text

        )

    def slug(
        self,
        text: str
    ) -> str:
        """
        Generate slug.
        """

        text = self.clean(

            text

        ).lower()

        text = re.sub(

            r"[^a-z0-9]+",

            "-",

            text

        )

        return text.strip(

            "-"

        )

    def safe_filename(
        self,
        filename: str
    ) -> str:
        """
        Safe filename.
        """

        return re.sub(

            r'[\\/:*?"<>|]',

            "_",

            filename

        )

    def truncate(
        self,
        text: str,
        length: int = 100
    ) -> str:
        """
        Truncate string.
        """

        if len(

            text

        ) <= length:

            return text

        return (

            text[:length]

            + "..."

        )

    def starts_with(
        self,
        text: str,
        prefix: str
    ) -> bool:

        return text.startswith(

            prefix

        )

    def ends_with(
        self,
        text: str,
        suffix: str
    ) -> bool:

        return text.endswith(

            suffix

        )

    def contains(
        self,
        text: str,
        value: str
    ) -> bool:

        return value in text

    def reverse(
        self,
        text: str
    ) -> str:

        return text[::-1]

    def is_empty(
        self,
        text: str
    ) -> bool:

        return not text.strip()

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "String Utils",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "StringUtils("

            "Enterprise Version)"

        )


string_utils = StringUtils()