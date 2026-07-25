"""
CyberMind AI

QR Scanner

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from pathlib import Path

from core.logger import logger

from services.qr_service import (
    qr_service
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


class QRScanner:
    """
    Enterprise QR Scanner.

    Responsibilities

    • QR Validation

    • QR Decode

    • URL Detection

    • Risk Analysis

    • Recommendation

    • Explain AI

    • Analytics
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "QR Scanner initialized."

        )

    def validate(
        self,
        image_path: str
    ) -> bool:
        """
        Validate QR image.
        """

        return (

            Path(

                image_path

            ).is_file()

        )

    def analyze(
        self,
        image_path: str
    ) -> dict[str, Any]:
        """
        Analyze QR image.
        """

        if not self.validate(

            image_path

        ):

            return {

                "success": False,

                "scanner": "qr",

                "message": "QR image not found."

            }

        logger.info(

            "QR scan started : %s",

            image_path

        )

        analysis = qr_service.analyze(
            image_path
        )

        decoded_text = analysis.get("decoded_text", "") or analysis.get("payload", "")

        if decoded_text:
            try:
                from services.qr_redirect_service import qr_redirect_service
                if "http://" in decoded_text or "https://" in decoded_text:
                    analysis["qr_redirect"] = qr_redirect_service.analyze_url(decoded_text)
            except Exception as exc:
                logger.warning("QR redirect analysis failed: %s", exc)

            try:
                from services.fake_payment_qr_service import fake_payment_qr_service
                analysis["payment_qr"] = fake_payment_qr_service.analyze_payload(decoded_text)
            except Exception as exc:
                logger.warning("Fake payment QR analysis failed: %s", exc)

        try:
            from services.lexical_keyword_service import lexical_keyword_service
            analysis["lexical_keywords"] = lexical_keyword_service.check_suspicious_keywords(decoded_text or image_path)
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
            "scanner": "qr",
            "image": image_path,
            "analysis": analysis,
            "risk": risk,
            "recommendation": recommendation,
            "explain_ai": explanation
        }

        try:
            from modules.mitre_mapper import mitre_mapper
            result["mitre_attack"] = mitre_mapper.map_findings(result)
        except Exception as exc:
            logger.warning("MITRE mapping failed for QR scanner: %s", exc)

        analytics_engine.add(

            result

        )

        logger.info(

            "QR scan completed."

        )

        return result

    def analyze_batch(
        self,
        images: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple QR images.
        """

        return [

            self.analyze(

                image

            )

            for image

            in images

        ]

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "QR Validation",

            "QR Decoding",

            "URL Detection",

            "Risk Analysis",

            "Recommendation",

            "Explain AI",

            "Analytics",

            "Batch Analysis"

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "QR Scanner",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "QRScanner("

            "Enterprise Version)"

        )


qr_scanner = QRScanner()