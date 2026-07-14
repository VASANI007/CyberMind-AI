"""
CyberMind AI

Date Utilities

Enterprise Production Version
"""

from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone
)

from typing import Any

from core.logger import logger


class DateUtils:
    """
    Enterprise Date Utility.

    Responsibilities

    • Current Date

    • Current Time

    • Formatting

    • Parsing

    • Date Difference

    • Timestamp

    • UTC Support
    """

    DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self
    ) -> None:

        logger.info(

            "Date Utils initialized."

        )

    def now(
        self
    ) -> datetime:
        """
        Current local datetime.
        """

        return datetime.now()

    def utc_now(
        self
    ) -> datetime:
        """
        Current UTC datetime.
        """

        return datetime.now(

            timezone.utc

        )

    def today(
        self
    ) -> str:
        """
        Today's date.
        """

        return self.now().strftime(

            "%Y-%m-%d"

        )

    def current_time(
        self
    ) -> str:
        """
        Current time.
        """

        return self.now().strftime(

            "%H:%M:%S"

        )

    def timestamp(
        self
    ) -> float:
        """
        Unix timestamp.
        """

        return self.now().timestamp()

    def format(
        self,
        value: datetime,
        pattern: str = DEFAULT_FORMAT
    ) -> str:
        """
        Format datetime.
        """

        return value.strftime(

            pattern

        )

    def parse(
        self,
        value: str,
        pattern: str = DEFAULT_FORMAT
    ) -> datetime:
        """
        Parse datetime.
        """

        return datetime.strptime(

            value,

            pattern

        )

    def days_between(
        self,
        start: datetime,
        end: datetime
    ) -> int:
        """
        Days between dates.
        """

        return abs(

            (end - start).days

        )

    def add_days(
        self,
        value: datetime,
        days: int
    ) -> datetime:
        """
        Add days.
        """

        return value + timedelta(

            days=days

        )

    def subtract_days(
        self,
        value: datetime,
        days: int
    ) -> datetime:
        """
        Subtract days.
        """

        return value - timedelta(

            days=days

        )

    def is_today(
        self,
        value: datetime
    ) -> bool:
        """
        Check today's date.
        """

        return (

            value.date()

            ==

            self.now().date()

        )

    def is_future(
        self,
        value: datetime
    ) -> bool:
        """
        Check future date.
        """

        return value > self.now()

    def is_past(
        self,
        value: datetime
    ) -> bool:
        """
        Check past date.
        """

        return value < self.now()

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Date Utils",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "DateUtils("

            "Enterprise Version)"

        )


date_utils = DateUtils()