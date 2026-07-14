"""
CyberMind AI

Domain Service

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger

from services.blacklist_service import (
    blacklist_service
)

from services.dns_service import (
    dns_service
)

from services.geo_service import (
    geo_service
)

from services.ipinfo_service import (
    ipinfo_service
)

from services.reputation_service import (
    reputation_service
)

from services.ssl_service import (
    ssl_service
)

from services.whois_service import (
    whois_service
)


class DomainService:
    """
    Enterprise Domain Analysis Service.

    Responsibilities

    • Domain Validation

    • DNS Analysis

    • WHOIS Analysis

    • SSL Analysis

    • Geo Location

    • IP Information

    • Blacklist Detection

    • Reputation Analysis

    • Final Domain Report
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "Domain Service initialized."

        )

    def normalize(self, domain: str) -> str:
        """
        Normalize domain.
        """
        return self._normalize_domain(domain)

    def _normalize_domain(
        self,
        domain: str
    ) -> str:
        """
        Normalize domain.
        """

        domain = domain.strip().lower()

        if domain.startswith(

            "http://"

        ):

            domain = domain[7:]

        elif domain.startswith(

            "https://"

        ):

            domain = domain[8:]

        domain = domain.split(

            "/"

        )[0]

        return domain

    def validate(self, domain: str) -> bool:
        """
        Validate domain.
        """
        return self._validate_domain(domain)

    def _validate_domain(
        self,
        domain: str
    ) -> bool:
        """
        Validate domain.
        """

        domain = self._normalize_domain(

            domain

        )

        return (

            "." in domain

            and

            " " not in domain

            and

            len(

                domain

            ) > 3

        )

    def _empty_response(
        self,
        domain: str,
        message: str
    ) -> dict[str, Any]:
        """
        Standard error response.
        """

        return {

            "success": False,

            "domain": domain,

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

            "domain": "",

            "ip": "",

            "dns": {},

            "whois": {},

            "ssl": {},

            "geo": {},

            "ip_information": {},

            "blacklist": {},

            "reputation": {}

        }

    def _hostname(
        self,
        domain: str
    ) -> str:
        """
        Return normalized hostname.
        """

        return self._normalize_domain(

            domain

        )
        




    def dns(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        DNS analysis.
        """

        try:

            return dns_service.analyze(

                self._hostname(

                    domain

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def whois(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        WHOIS analysis.
        """

        try:

            return whois_service.analyze(

                self._hostname(

                    domain

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def ssl(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        SSL analysis.
        """

        try:

            return ssl_service.analyze(

                self._hostname(

                    domain

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def geo(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        Geo location.
        """

        try:

            return geo_service.analyze(

                self._hostname(

                    domain

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def ip_information(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        IP information.
        """

        try:

            return ipinfo_service.analyze(

                self._hostname(

                    domain

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return {}

    def blacklist(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        Blacklist analysis.
        """

        try:

            return blacklist_service.analyze(

                self._hostname(

                    domain

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
        domain: str
    ) -> dict[str, Any]:
        """
        Analyze domain.
        """

        try:

            domain = self._normalize_domain(

                domain

            )

        except Exception as error:

            logger.exception(

                error

            )

            return self._empty_response(

                str(domain),

                str(error)

            )

        if not self._validate_domain(

            domain

        ):

            logger.warning(

                "Invalid domain : %s",

                domain

            )

            return self._empty_response(

                domain,

                "Invalid domain."

            )

        logger.info(

            "Starting domain analysis : %s",

            domain

        )

        report = self._success_response()

        report["domain"] = domain

        report["dns"] = self.dns(

            domain

        )

        report["whois"] = self.whois(

            domain

        )

        report["ssl"] = self.ssl(

            domain

        )

        report["geo"] = self.geo(

            domain

        )

        report["ip_information"] = (

            self.ip_information(

                domain

            )

        )

        report["blacklist"] = (

            self.blacklist(

                domain

            )

        )

        report["reputation"] = (

            self.reputation(

                report

            )

        )

        ip_information = report.get(

            "ip_information",

            {}

        )

        report["ip"] = (

            ip_information.get(

                "ip"

            )

            or

            ip_information.get(

                "ip_address"

            )

            or

            ""

        )

        logger.info(

            "Domain analysis completed."

        )

        return report

    def analyze_batch(
        self,
        domains: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple domains.
        """

        results = []

        for domain in domains:

            results.append(

                self.analyze(

                    domain

                )

            )

        return results
    

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Service health information.
        """

        return {

            "service":

                "Domain Service",

            "status":

                "Healthy",

            "version":

                "2.0",

            "modules": {

                "dns": True,

                "whois": True,

                "ssl": True,

                "geo": True,

                "ip_information": True,

                "blacklist": True,

                "reputation": True

            }

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported domain analysis features.
        """

        return [

            "DNS",

            "WHOIS",

            "SSL",

            "Geo Location",

            "IP Information",

            "Blacklist",

            "Reputation",

            "Batch Analysis"

        ]

    def __repr__(
        self
    ) -> str:
        """
        String representation.
        """

        return (

            "DomainService("

            "Enterprise Version)"

        )


domain_service = DomainService()