"""
CyberMind AI

Explain AI Engine

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger


class ExplainAI:
    """
    Enterprise Explain AI Engine.

    Responsibilities

    • Explain Scan Results

    • Explain Risk

    • Explain Reputation

    • Explain Detection

    • Human Readable Output
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "Explain AI initialized."

        )

    def explain(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate human readable explanation.
        """

        explanation = []

        reputation = report.get(

            "reputation",

            {}

        )

        blacklist = report.get(

            "blacklist",

            {}

        )

        ssl = report.get(

            "ssl",

            {}

        )

        google = report.get(

            "google_safe_browsing",

            {}

        )

        virustotal = report.get(

            "virustotal",

            {}

        )

        risk = report.get(

            "risk",

            {}

        )

        level = risk.get(

            "level",

            "Unknown"

        )

        explanation.append(

            f"Overall Risk Level: {level}"

        )

        if reputation.get(

            "score",

            100

        ) >= 80:

            explanation.append(

                "The reputation score indicates this resource is generally trustworthy."

            )

        else:

            explanation.append(

                "The reputation score is below the recommended threshold."

            )

        if blacklist.get(

            "detected",

            False

        ):

            explanation.append(

                "This resource appears in one or more blacklist databases."

            )

        if not ssl.get(

            "valid",

            True

        ):

            explanation.append(

                "The SSL certificate is invalid, expired, or unavailable."

            )

        if google.get(

            "malicious",

            False

        ):

            explanation.append(

                "Google Safe Browsing identified this resource as potentially unsafe."

            )

        malicious = virustotal.get(

            "malicious",

            0

        )

        if malicious > 0:

            explanation.append(

                f"{malicious} security vendors detected this resource."

            )

        if len(

            explanation

        ) == 1:

            explanation.append(

                "No significant security issues were identified."

            )

        return {

            "summary":

                explanation[0],

            "details":

                explanation

        }

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Engine health.
        """

        return {

            "service":

                "Explain AI",

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

            "Risk Explanation",

            "Reputation Explanation",

            "SSL Explanation",

            "Blacklist Explanation",

            "VirusTotal Explanation",

            "Google Safe Browsing Explanation"

        ]

    def __repr__(
        self
    ) -> str:

        return (

            "ExplainAI("

            "Enterprise Version)"

        )


explain_ai = ExplainAI()