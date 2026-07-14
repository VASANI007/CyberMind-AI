"""
CyberMind AI

IP Scanner

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger

from services.ip_service import (
    ip_service
)

from modules.risk_engine import (
    risk_engine
)

from modules.recommendation import (
    recommendation_engine
)

from modules.explain_ai import (
    explain_ai
)

from modules.analytics_engine import (
    analytics_engine
)


class IPScanner:
    """
    Enterprise IP Scanner.

    Responsibilities

    • IP Validation

    • IP Analysis

    • Risk Analysis

    • Recommendation

    • Explain AI

    • Analytics
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "IP Scanner initialized."

        )

    def validate(
        self,
        ip: str
    ) -> bool:
        """
        Validate IP.
        """

        return ip_service.validate(

            ip

        )

    def analyze(
        self,
        ip: str
    ) -> dict[str, Any]:
        """
        Analyze IP address.
        """

        if not self.validate(

            ip

        ):

            return {

                "success": False,

                "scanner": "ip",

                "message": "Invalid IP address."

            }

        logger.info(

            "IP scan started : %s",

            ip

        )

        analysis = ip_service.analyze(

            ip

        )

        risk = risk_engine.calculate(

            analysis

        )

        analysis["risk"] = risk

        recommendation = (

            recommendation_engine.generate(

                analysis

            )

        )

        explanation = (

            explain_ai.explain(

                analysis

            )

        )

        result = {

            "success": True,

            "scanner": "ip",

            "ip": ip,

            "analysis": analysis,

            "risk": risk,

            "recommendation": recommendation,

            "explain_ai": explanation

        }

        analytics_engine.add(

            result

        )

        logger.info(

            "IP scan completed."

        )

        return result

    def analyze_batch(
        self,
        ips: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple IP addresses.
        """

        return [

            self.analyze(

                ip

            )

            for ip

            in ips

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service": "IP Scanner",

            "status": "Healthy",

            "version": "2.0"

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "IPv4 Analysis",

            "IPv6 Analysis",

            "Geo Location",

            "WHOIS",

            "Blacklist",

            "AbuseIPDB",

            "IPInfo",

            "Risk Analysis",

            "Recommendation",

            "Explain AI",

            "Analytics",

            "Batch Analysis"

        ]

    def __repr__(
        self
    ) -> str:

        return (

            "IPScanner("

            "Enterprise Version)"

        )


ip_scanner = IPScanner()