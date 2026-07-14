"""
CyberMind AI

URL Service

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from core.logger import logger

from services.blacklist_service import blacklist_service
from services.dns_service import dns_service
from services.google_safe_browsing_service import (
    google_safe_browsing_service
)
from services.metadata_service import metadata_service
from services.reputation_service import reputation_service
from services.security_headers_service import (
    security_headers_service
)
from services.ssl_service import ssl_service
from services.url_feature_service import (
    url_feature_service
)
from services.virustotal_service import (
    virustotal_service
)
from services.whois_service import whois_service


class URLService:
    """
    Enterprise URL Analysis Service.

    Responsibilities

    • URL Validation
    • Metadata Collection
    • Feature Extraction
    • DNS Analysis
    • WHOIS Analysis
    • SSL Analysis
    • Security Header Analysis
    • Blacklist Detection
    • Google Safe Browsing
    • VirusTotal Analysis
    • Reputation Analysis
    • Final Security Report
    """

    DEFAULT_SCHEME = "https://"

    def __init__(self) -> None:

        logger.info(
            "URL Service initialized."
        )

    def normalize(self, url: str) -> str:
        """
        Normalize URL using _normalize_url.
        """
        return self._normalize_url(url)

    def _normalize_url(
        self,
        url: str
    ) -> str:
        """
        Normalize URL.
        """

        if not isinstance(
            url,
            str
        ):
            raise TypeError(
                "URL must be string."
            )

        url = url.strip()

        if not url:

            raise ValueError(
                "URL cannot be empty."
            )

        if not url.startswith(
            (
                "http://",
                "https://"
            )
        ):
            url = (
                self.DEFAULT_SCHEME
                + url
            )

        return url

    def _parse_url(
        self,
        url: str
    ):

        return urlparse(
            self._normalize_url(
                url
            )
        )

    def hostname(self, url: str) -> str:
        """
        Return hostname.
        """
        return self._hostname(url)

    def _hostname(
        self,
        url: str
    ) -> str:
        """
        Return hostname.
        """

        parsed = self._parse_url(
            url
        )

        return (
            parsed.hostname
            or ""
        ).lower()

    def validate(self, url: str) -> bool:
        """
        Validate URL.
        """
        return self._is_valid(url)

    def _is_valid(
        self,
        url: str
    ) -> bool:
        """
        Validate URL.
        """

        try:

            parsed = self._parse_url(
                url
            )

            return all(
                [
                    parsed.scheme,
                    parsed.netloc
                ]
            )

        except Exception:

            return False

    def _empty_response(
        self,
        url: str,
        message: str
    ) -> dict[str, Any]:
        """
        Standard error response.
        """

        return {

            "success": False,

            "url": url,

            "message": message

        }

    def _success_response(
        self
    ) -> dict[str, Any]:
        """
        Base response object.
        """

        return {

            "success": True,

            "url": "",

            "hostname": "",

            "metadata": {},

            "features": {},

            "dns": {},

            "whois": {},

            "ssl": {},

            "security_headers": {},

            "blacklist": {},

            "google_safe_browsing": {},

            "virustotal": {},

            "reputation": {}

        }
        
    def metadata(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Collect URL metadata.
        """

        try:

            return metadata_service.extract(

                self._normalize_url(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def features(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Extract ML features.
        """

        try:

            return url_feature_service.extract_features(

                self._normalize_url(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def dns(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        DNS analysis.
        """

        try:

            return dns_service.analyze(

                self._hostname(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def whois(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        WHOIS analysis.
        """

        try:

            return whois_service.analyze(

                self._hostname(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def ssl(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        SSL analysis.
        """

        try:

            return ssl_service.analyze(

                self._hostname(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def security_headers(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Security header analysis.
        """

        try:

            return security_headers_service.analyze(

                self._normalize_url(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def blacklist(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Blacklist analysis.
        """

        try:

            return blacklist_service.analyze(

                self._normalize_url(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def google_safe_browsing(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Google Safe Browsing analysis.
        """

        try:

            return google_safe_browsing_service.scan(

                self._normalize_url(url)

            )

        except Exception as error:

            logger.exception(error)

            return {}

    def virustotal(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        VirusTotal analysis.
        """

        try:

            return virustotal_service.scan_url(

                self._normalize_url(url)

            )

        except Exception as error:

            logger.exception(error)

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

            logger.exception(error)

            return {}
        
        
    def analyze(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Analyze URL and return
        complete security report.
        """

        try:

            url = self._normalize_url(

                url

            )

        except Exception as error:

            logger.exception(error)

            return self._empty_response(

                url=str(url),

                message=str(error)

            )

        if not self._is_valid(

            url

        ):

            logger.warning(

                "Invalid URL : %s",

                url

            )

            return self._empty_response(

                url,

                "Invalid URL."

            )

        logger.info(

            "Starting URL Analysis : %s",

            url

        )

        report = self._success_response()

        report["url"] = url

        report["hostname"] = self._hostname(

            url

        )

        report["metadata"] = self.metadata(

            url

        )

        report["features"] = self.features(

            url

        )

        report["dns"] = self.dns(

            url

        )

        report["whois"] = self.whois(

            url

        )

        report["ssl"] = self.ssl(

            url

        )

        report["security_headers"] = self.security_headers(

            url

        )

        report["blacklist"] = self.blacklist(

            url

        )

        report["google_safe_browsing"] = (

            self.google_safe_browsing(

                url

            )

        )

        report["virustotal"] = self.virustotal(

            url

        )

        report["reputation"] = self.reputation(

            report

        )

        logger.info(

            "Analysis Completed."

        )

        return report
    
    def analyze_batch(
        self,
        urls: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple URLs.
        """

        logger.info(

            "Batch analysis started."

        )

        results = []

        for url in urls:

            results.append(

                self.analyze(url)

            )

        logger.info(

            "Batch analysis completed."

        )

        return results

    def analyze_dataframe(
        self,
        dataframe
    ):
        """
        Analyze URLs from DataFrame.

        Expected column:
        url
        """

        if "url" not in dataframe.columns:

            raise ValueError(

                "DataFrame must contain 'url' column."

            )

        reports = self.analyze_batch(

            dataframe["url"].tolist()

        )

        dataframe = dataframe.copy()

        dataframe["report"] = reports

        return dataframe

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Service health information.
        """

        return {

            "service": "URL Service",

            "status": "Healthy",

            "feature_engine": "Ready",

            "dns": "Ready",

            "whois": "Ready",

            "ssl": "Ready",

            "security_headers": "Ready",

            "blacklist": "Ready",

            "google_safe_browsing": "Ready",

            "virustotal": "Ready",

            "reputation": "Ready"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "URLService("

            "Enterprise Version)"

        )


url_service = URLService()