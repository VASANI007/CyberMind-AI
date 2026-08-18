"""
CyberMind AI

Phone Threat Intelligence & Scam Risk Scanner

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any
from core.logger import logger
from services.phone_service import phone_service
from modules.risk_engine import risk_engine
from modules.recommendation import recommendation_engine
from modules.explain_ai import explain_ai
from modules.analytics_engine import analytics_engine


class PhoneScanner:
    """
    Enterprise Phone Threat Intelligence Scanner.
    """

    def __init__(self) -> None:
        logger.info("Phone Scanner initialized.")

    def analyze(self, phone_number: str) -> dict[str, Any]:
        """
        Analyze a phone number for threat intelligence and scam risk.
        """
        from core.validator import validate_scanner_input
        is_valid, err_msg = validate_scanner_input("Phone Threat Intelligence", phone_number)
        if not is_valid:
            return {
                "success": False,
                "scanner": "phone",
                "message": err_msg or "Invalid phone number format."
            }

        logger.info("Phone threat scan started: %s", phone_number)
        analysis = phone_service.analyze(phone_number)

        # Unified Risk Engine integration
        risk = risk_engine.calculate(analysis)

        # Align overall risk score with phone fraud score if specific threat signals present
        if analysis.get("fraud_score", 0) > risk.get("score", 0):
            risk["score"] = analysis["fraud_score"]
            risk["level"] = risk_engine.level(risk["score"])

        analysis["risk"] = risk

        recommendation = recommendation_engine.generate(analysis)
        explanation = explain_ai.explain(analysis)

        result = {
            "success": True,
            "scanner": "phone",
            "phone": phone_number,
            "analysis": analysis,
            "risk": risk,
            "recommendation": recommendation,
            "explain_ai": explanation
        }

        analytics_engine.add(result)
        logger.info("Phone threat scan completed for %s", phone_number)
        return result

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """
        return {
            "service": "Phone Scanner",
            "status": "Healthy",
            "version": "2.0"
        }

    def supported_features(self) -> list[str]:
        """
        Supported features.
        """
        return [
            "Phone Validation",
            "Telecom & Carrier Analysis",
            "VoIP & Prepaid Detection",
            "IPQS Threat Intelligence",
            "Scam & Abuse Risk Scoring",
            "Report Number Feature",
            "Unified Cyber Risk Engine"
        ]

    def __repr__(self) -> str:
        return "PhoneScanner(Enterprise Version)"


phone_scanner = PhoneScanner()
