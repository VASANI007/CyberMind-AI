"""
CyberMind AI

Email Service

Enterprise Production Version
"""

from __future__ import annotations

import re

from typing import Any

from core.logger import logger

from services.dns_service import (
    dns_service
)

from services.domain_service import (
    domain_service
)

from services.blacklist_service import (
    blacklist_service
)

from services.reputation_service import (
    reputation_service
)


class EmailService:
    """
    Enterprise Email Analysis Service.

    Responsibilities

    • Email Validation

    • Domain Analysis

    • DNS Analysis

    • MX Record Verification

    • SPF Detection

    • DKIM Detection

    • DMARC Detection

    • Blacklist Detection

    • Reputation Analysis

    • Final Email Report
    """

    EMAIL_PATTERN = re.compile(

        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    )

    def __init__(
        self
    ) -> None:

        logger.info(

            "Email Service initialized."

        )

    def normalize(self, email: str) -> str:
        """
        Normalize email.
        """
        return self._normalize_email(email)

    def _normalize_email(
        self,
        email: str
    ) -> str:
        """
        Normalize email.
        """

        return email.strip().lower()

    def validate(self, email: str) -> bool:
        """
        Validate email.
        """
        return self._validate_email(email)

    def _validate_email(
        self,
        email: str
    ) -> bool:
        """
        Validate email.
        """

        email = self._normalize_email(

            email

        )

        return bool(

            self.EMAIL_PATTERN.fullmatch(

                email

            )

        )

    def _domain(
        self,
        email: str
    ) -> str:
        """
        Extract email domain.
        """

        return self._normalize_email(

            email

        ).split(

            "@"

        )[-1]

    def _empty_response(
        self,
        email: str,
        message: str
    ) -> dict[str, Any]:
        """
        Standard error response.
        """

        return {

            "success": False,

            "email": email,

            "message": message

        }

    def _success_response(
        self
    ) -> dict[str, Any]:
        """
        Standard response.
        """

        return {

            "success": True,

            "email": "",

            "domain": "",

            "domain_analysis": {},

            "dns": {},

            "mx": {},

            "spf": {},

            "dkim": {},

            "dmarc": {},

            "blacklist": {},

            "reputation": {}

        }
        


    def domain_analysis(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        Analyze email domain.
        """

        try:

            return domain_service.analyze(

                self._domain(

                    email

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def dns(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        DNS analysis.
        """

        try:

            return dns_service.analyze(

                self._domain(

                    email

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def mx(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        MX record analysis.
        """

        try:

            dns = self.dns(

                email

            )

            return {

                "available":

                    bool(

                        dns.get(

                            "mx_records",

                            []

                        )

                    ),

                "records":

                    dns.get(

                        "mx_records",

                        []

                    )

            }

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def spf(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        SPF analysis.
        """

        try:

            dns = self.dns(

                email

            )

            txt = dns.get(

                "txt_records",

                []

            )

            record = next(

                (

                    value

                    for value in txt

                    if value.startswith(

                        "v=spf1"

                    )

                ),

                ""

            )

            return {

                "found":

                    bool(

                        record

                    ),

                "record":

                    record

            }

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def dkim(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        DKIM analysis.
        """

        try:

            dns = self.dns(

                email

            )

            txt = dns.get(

                "txt_records",

                []

            )

            record = next(

                (

                    value

                    for value in txt

                    if "dkim"

                    in

                    value.lower()

                ),

                ""

            )

            return {

                "found":

                    bool(

                        record

                    ),

                "record":

                    record

            }

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def dmarc(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        DMARC analysis.
        """

        try:

            dns = self.dns(

                email

            )

            txt = dns.get(

                "txt_records",

                []

            )

            record = next(

                (

                    value

                    for value in txt

                    if value.startswith(

                        "v=DMARC1"

                    )

                ),

                ""

            )

            return {

                "found":

                    bool(

                        record

                    ),

                "record":

                    record

            }

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def blacklist(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        Blacklist analysis.
        """

        try:

            return blacklist_service.analyze(

                self._domain(

                    email

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def reputation(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Reputation analysis.
        """

        try:

            return reputation_service.analyze(

                report

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}
        
        
    
    def analyze(
        self,
        email: str
    ) -> dict[str, Any]:
        """
        Analyze email.
        """

        try:

            email = self._normalize_email(

                email

            )

        except Exception as error:

            logger.exception(

                error

            )

            return self._empty_response(

                str(email),

                str(error)

            )

        if not self._validate_email(

            email

        ):

            logger.warning(

                "Invalid email : %s",

                email

            )

            return self._empty_response(

                email,

                "Invalid email."

            )

        logger.info(

            "Starting email analysis : %s",

            email

        )

        report = self._success_response()

        report["email"] = email

        report["domain"] = self._domain(

            email

        )

        report["domain_analysis"] = (

            self.domain_analysis(

                email

            )

        )

        dns_report = self.dns(

            email

        )

        report["dns"] = dns_report

        txt_records = dns_report.get(

            "txt_records",

            []

        )

        report["mx"] = {

            "available":

                bool(

                    dns_report.get(

                        "mx_records",

                        []

                    )

                ),

            "records":

                dns_report.get(

                    "mx_records",

                    []

                )

        }

        spf_record = next(

            (

                record

                for record

                in txt_records

                if record.startswith(

                    "v=spf1"

                )

            ),

            ""

        )

        report["spf"] = {

            "found":

                bool(

                    spf_record

                ),

            "record":

                spf_record

        }

        dkim_record = next(

            (

                record

                for record

                in txt_records

                if "dkim"

                in record.lower()

            ),

            ""

        )

        report["dkim"] = {

            "found":

                bool(

                    dkim_record

                ),

            "record":

                dkim_record

        }

        dmarc_record = next(

            (

                record

                for record

                in txt_records

                if record.startswith(

                    "v=DMARC1"

                )

            ),

            ""

        )

        report["dmarc"] = {

            "found":

                bool(

                    dmarc_record

                ),

            "record":

                dmarc_record

        }

        report["blacklist"] = (

            self.blacklist(

                email

            )

        )

        report["reputation"] = (

            self.reputation(

                report

            )

        )

        logger.info(

            "Email analysis completed."

        )

        return report

    def analyze_batch(
        self,
        emails: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple email addresses.
        """

        return [

            self.analyze(

                email

            )

            for email

            in emails

        ]
        
        
    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Service health information.
        """

        return {

            "service":

                "Email Service",

            "status":

                "Healthy",

            "version":

                "2.0",

            "modules": {

                "domain_analysis": True,

                "dns": True,

                "mx": True,

                "spf": True,

                "dkim": True,

                "dmarc": True,

                "blacklist": True,

                "reputation": True

            }

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported email analysis features.
        """

        return [

            "Email Validation",

            "Domain Analysis",

            "DNS Analysis",

            "MX Record",

            "SPF Record",

            "DKIM Record",

            "DMARC Record",

            "Blacklist Detection",

            "Reputation Analysis",

            "Batch Analysis"

        ]

    def __repr__(
        self
    ) -> str:
        """
        String representation.
        """

        return (

            "EmailService("

            "Enterprise Version)"

        )


email_service = EmailService()