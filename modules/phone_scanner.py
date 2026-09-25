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

        # Phone-specific Risk Engine integration
        # NOTE: Generic risk_engine.calculate() is designed for URL/domain/email with reputation,
        # blacklist, ssl, google_safe_browsing, virustotal sources. For phone scans, none of those
        # exist → missing_count=5 → always score=15, data_completeness=0%, level="Unverified".
        # Instead, use phone_service's own rule_score (stored as fraud_score) directly.
        phone_fraud_score = analysis.get("fraud_score", 0)
        scam_risk = analysis.get("scam_risk", "Low")

        # Map phone scam_risk to standard risk level
        _scam_to_level = {
            "Low": "Safe",
            "Unverified": "Low",   # IPQS data unavailable — cannot confirm safe, show cautious Low
            "Medium": "Medium",
            "High": "High",
            "Critical": "Critical",
        }
        phone_risk_level = _scam_to_level.get(scam_risk, "Low")

        # Build risk dict compatible with run_scan() expectations
        risk = {
            "score": phone_fraud_score,
            "level": phone_risk_level,
            "confidence": 75.0 if (
                analysis.get("abstract_phone_integrated")
                or analysis.get("numverify_integrated")
                or analysis.get("verificaremails_integrated")
                or analysis.get("veriphone_integrated")
                or analysis.get("ipqs_integrated")
            ) else 50.0,
            "data_completeness": 100.0,
            "sources_present": 1,
            "sources_expected": 1,
            "reasons": analysis.get("reasons", []),
            "breakdown": {
                "phone_fraud_score": phone_fraud_score,
                "scam_risk": scam_risk,
            },
            "consensus": {
                "sources_checked": 1,
                "sources_flagged": 1 if phone_fraud_score >= 50 else 0,
                "consensus_ratio": 1.0 if phone_fraud_score >= 50 else 0.0,
                "summary": f"Phone intelligence score: {phone_fraud_score}/100"
            }
        }

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
            "AbstractAPI / Numverify / VerificarEmails Phone Intelligence",
            "Scam & Abuse Risk Scoring",
            "Report Number Feature",
            "Unified Cyber Risk Engine"
        ]

    def __repr__(self) -> str:
        return "PhoneScanner(Enterprise Version)"


phone_scanner = PhoneScanner()
