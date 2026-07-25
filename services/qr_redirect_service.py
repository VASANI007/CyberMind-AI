"""
CyberMind AI
QR Redirect Service
Analyzes decoded QR URLs by running them through redirect chain analysis.
Offline — reuses redirect_chain_service.
"""

from __future__ import annotations

from typing import Any

from core.logger import logger


class QRRedirectService:
    """
    Analyzes URLs decoded from QR codes by following
    their redirect chain and assessing risk.
    """

    @property
    def name(self) -> str:
        return "qr_redirect_service"

    def analyze_url(self, url: str) -> dict[str, Any]:
        """
        Analyze a decoded QR URL.

        Returns
        -------
        dict with keys:
            redirect_chain : dict  — from redirect_chain_service
            is_suspicious  : bool
            risk_factors   : list[str]
        """
        risk_factors = []

        # Run redirect chain
        chain_result = {"chain": [], "hops": 0, "final": url, "loop": False}
        try:
            from services.redirect_chain_service import redirect_chain_service
            chain_result = redirect_chain_service.follow(url)
        except Exception as exc:
            logger.warning("QR redirect chain error: %s", exc)
            risk_factors.append(f"Redirect analysis failed: {exc}")

        # Assess risk from chain
        if chain_result.get("hops", 0) > 3:
            risk_factors.append(f"Excessive redirects: {chain_result['hops']} hops")

        if chain_result.get("loop"):
            risk_factors.append("Redirect loop detected")

        final = chain_result.get("final", "")
        if final != url:
            risk_factors.append(f"Final destination differs from QR URL")

        # Check for suspicious patterns in final URL
        suspicious_patterns = [
            ("bit.ly", "URL shortener in chain"),
            ("tinyurl", "URL shortener in chain"),
            (".tk", "Free TLD (.tk)"),
            (".ml", "Free TLD (.ml)"),
            (".ga", "Free TLD (.ga)"),
            (".cf", "Free TLD (.cf)"),
            ("login", "Login-related URL"),
            ("signin", "Sign-in related URL"),
            ("verify", "Verification-related URL"),
            ("secure", "Security-themed URL"),
            ("update", "Update-themed URL"),
        ]

        for pattern, desc in suspicious_patterns:
            if pattern in final.lower():
                risk_factors.append(desc)

        return {
            "redirect_chain": chain_result,
            "is_suspicious": len(risk_factors) > 0,
            "risk_factors": risk_factors,
            "risk_contribution": min(len(risk_factors) * 10, 40),
        }

    def analyze(self, url: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.analyze_url(url)

    def health_check(self) -> dict[str, Any]:
        return {"service": "QR Redirect Service", "status": "Healthy"}


qr_redirect_service = QRRedirectService()
