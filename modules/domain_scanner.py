"""
CyberMind AI

Domain Scanner

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger

from services.domain_service import (
    domain_service
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


class DomainScanner:
    """
    Enterprise Domain Scanner.

    Responsibilities

    • Domain Validation

    • Domain Analysis

    • Risk Analysis

    • Recommendation

    • Explain AI

    • Analytics
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "Domain Scanner initialized."

        )

    def validate(
        self,
        domain: str
    ) -> bool:
        """
        Validate domain.
        """

        return domain_service._validate_domain(

            domain

        )

    def normalize(
        self,
        domain: str
    ) -> str:
        """
        Normalize domain.
        """

        return domain_service._normalize_domain(

            domain

        )

    def analyze(
        self,
        domain: str
    ) -> dict[str, Any]:
        """
        Analyze domain.
        """

        domain = self.normalize(

            domain

        )

        if not self.validate(

            domain

        ):

            return {

                "success": False,

                "scanner": "domain",

                "message": "Invalid domain."

            }

        logger.info(

            "Domain scan started : %s",

            domain

        )

        analysis = domain_service.analyze(
            domain
        )

        try:
            from services.subdomain_discovery_service import subdomain_discovery_service
            analysis["subdomain_discovery"] = subdomain_discovery_service.discover(domain)
        except Exception as exc:
            logger.warning("Subdomain discovery failed for domain scanner: %s", exc)

        try:
            from services.lexical_keyword_service import lexical_keyword_service
            analysis["lexical_keywords"] = lexical_keyword_service.check_suspicious_keywords(domain)
        except Exception as e:
            logger.warning("Lexical keyword check failed: %s", e)

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
            "scanner": "domain",
            "domain": domain,
            "analysis": analysis,
            "risk": risk,
            "recommendation": recommendation,
            "explain_ai": explanation
        }

        try:
            from modules.mitre_mapper import mitre_mapper
            result["mitre_attack"] = mitre_mapper.map_findings(result)
        except Exception as exc:
            logger.warning("MITRE mapping failed for domain scanner: %s", exc)

        analytics_engine.add(

            result

        )

        logger.info(

            "Domain scan completed."

        )

        return result

    def analyze_batch(
        self,
        domains: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple domains.
        """

        return [

            self.analyze(

                domain

            )

            for domain

            in domains

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Domain Scanner",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "Domain Validation",

            "Domain Analysis",

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

            "DomainScanner("

            "Enterprise Version)"

        )


domain_scanner = DomainScanner()