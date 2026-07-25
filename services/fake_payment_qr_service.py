"""
CyberMind AI
Fake Payment QR Service
Detects potentially fraudulent UPI/payment QR codes.
Offline — rule-based matching against static patterns.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from core.logger import logger


class FakePaymentQRService:
    """
    Analyzes decoded QR payloads for suspicious payment patterns,
    particularly UPI payment QR codes.
    """

    # Known suspicious patterns in UPI QR codes
    SUSPICIOUS_UPI_PATTERNS = [
        # Unusually high amounts
        {"name": "High amount", "check": "amount_high", "threshold": 50000},
        # Missing merchant name
        {"name": "Missing merchant name", "check": "no_merchant"},
        # Suspicious payee names
        {"name": "Suspicious payee", "check": "suspicious_payee",
         "keywords": ["lottery", "prize", "winner", "reward", "cashback",
                       "refund", "bonus", "free", "claim", "urgent"]},
        # Non-standard UPI format
        {"name": "Malformed UPI", "check": "malformed"},
    ]

    @property
    def name(self) -> str:
        return "fake_payment_qr_service"

    def analyze_payload(self, payload: str) -> dict[str, Any]:
        """
        Analyze a QR decoded payload for payment fraud indicators.

        Returns
        -------
        dict with keys:
            is_payment      : bool  — True if UPI/payment payload
            is_suspicious   : bool
            warnings        : list[str]
            payment_details : dict  — parsed payment info (if UPI)
            risk_contribution : int
        """
        if not payload:
            return {
                "is_payment": False,
                "is_suspicious": False,
                "warnings": [],
                "payment_details": {},
                "risk_contribution": 0,
            }

        payload_lower = payload.lower().strip()

        # Check if this is a UPI payment
        if payload_lower.startswith("upi://pay"):
            return self._analyze_upi(payload)

        # Check for other payment patterns
        payment_keywords = ["payment", "pay.google", "phonepe", "paytm", "gpay"]
        is_payment = any(kw in payload_lower for kw in payment_keywords)

        if is_payment:
            return {
                "is_payment": True,
                "is_suspicious": False,
                "warnings": ["Non-UPI payment link detected — verify manually"],
                "payment_details": {"raw": payload[:100]},
                "risk_contribution": 5,
            }

        return {
            "is_payment": False,
            "is_suspicious": False,
            "warnings": [],
            "payment_details": {},
            "risk_contribution": 0,
        }

    def _analyze_upi(self, upi_uri: str) -> dict[str, Any]:
        """Analyze a UPI payment URI."""
        warnings = []

        try:
            parsed = urlparse(upi_uri)
            params = parse_qs(parsed.query)

            # Extract payment details
            payee = params.get("pa", [""])[0]
            payee_name = params.get("pn", [""])[0]
            amount = params.get("am", ["0"])[0]
            note = params.get("tn", [""])[0]
            currency = params.get("cu", ["INR"])[0]

            details = {
                "payee_address": payee,
                "payee_name": payee_name,
                "amount": amount,
                "note": note,
                "currency": currency,
            }

            # Check for suspicious indicators
            try:
                amt = float(amount)
                if amt > 50000:
                    warnings.append(f"⚠️ Unusually high amount: ₹{amt:,.0f}")
                if amt == 0:
                    warnings.append("⚠️ Zero amount — may be modified later")
            except (ValueError, TypeError):
                if amount:
                    warnings.append("⚠️ Invalid amount format")

            if not payee_name:
                warnings.append("⚠️ No merchant/payee name specified")

            if not payee or "@" not in payee:
                warnings.append("⚠️ Invalid or missing UPI address")

            # Check for suspicious keywords
            check_text = f"{payee_name} {note} {payee}".lower()
            sus_keywords = [
                "lottery", "prize", "winner", "reward", "cashback",
                "refund", "bonus", "free", "claim", "urgent", "lucky",
            ]
            for kw in sus_keywords:
                if kw in check_text:
                    warnings.append(f"⚠️ Suspicious keyword: '{kw}'")

            is_suspicious = len(warnings) > 0
            risk = min(len(warnings) * 12, 50) if is_suspicious else 0

            return {
                "is_payment": True,
                "is_suspicious": is_suspicious,
                "warnings": warnings,
                "payment_details": details,
                "risk_contribution": risk,
            }

        except Exception as exc:
            logger.warning("UPI parse error: %s", exc)
            return {
                "is_payment": True,
                "is_suspicious": True,
                "warnings": [f"⚠️ Malformed UPI URI: {exc}"],
                "payment_details": {"raw": upi_uri[:100]},
                "risk_contribution": 20,
            }

    def analyze(self, payload: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.analyze_payload(payload)

    def health_check(self) -> dict[str, Any]:
        return {"service": "Fake Payment QR Service", "status": "Healthy"}


fake_payment_qr_service = FakePaymentQRService()
