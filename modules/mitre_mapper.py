"""
CyberMind AI
MITRE ATT&CK Mapper
Maps scan findings to MITRE ATT&CK technique IDs.
Offline — uses local curated technique subset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "security"


class MITREMapper:
    """
    Maps CyberMind scan findings to relevant MITRE ATT&CK techniques.
    """

    def __init__(self) -> None:
        self._techniques: list[dict] = []
        self._load_techniques()

    def _load_techniques(self) -> None:
        path = _DATA_DIR / "mitre_attack_lite.json"
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self._techniques = json.load(f)
                logger.info(
                    "Loaded %d MITRE ATT&CK techniques.",
                    len(self._techniques),
                )
        except Exception as exc:
            logger.warning("MITRE techniques load error: %s", exc)

    @property
    def name(self) -> str:
        return "mitre_mapper"

    def map_findings(self, scan_result: dict) -> dict[str, Any]:
        """
        Map scan result findings to MITRE ATT&CK techniques.

        Returns
        -------
        dict with keys:
            techniques : list[dict] — id, name, tactic, description, relevance
            count      : int
        """
        matched = []

        # Extract signals from scan result
        signals = self._extract_signals(scan_result)

        for tech in self._techniques:
            triggers = tech.get("triggers", [])
            for trigger in triggers:
                if trigger in signals:
                    matched.append({
                        "id": tech.get("id", ""),
                        "name": tech.get("name", ""),
                        "tactic": tech.get("tactic", ""),
                        "description": tech.get("description", ""),
                        "url": f"https://attack.mitre.org/techniques/{tech.get('id', '')}/",
                        "relevance": trigger,
                    })
                    break  # One match per technique

        return {
            "techniques": matched[:10],
            "count": len(matched),
        }

    def _extract_signals(self, scan_result: dict) -> set[str]:
        """Extract signal keywords from a scan result."""
        signals = set()
        risk_score = scan_result.get("risk_score", 0)
        risk_level = scan_result.get("risk_level", "").lower()

        # High-level signals
        if risk_score >= 70:
            signals.add("high_risk")
        if risk_score >= 90:
            signals.add("critical_risk")

        # Result-specific signals
        result_data = scan_result.get("result", {})
        if isinstance(result_data, dict):
            # URL/Website specific
            if result_data.get("redirect_chain", {}).get("hops", 0) > 2:
                signals.add("redirect_chain")
            if result_data.get("js_behavior", {}).get("total", 0) > 0:
                signals.add("malicious_script")

            js_flags = result_data.get("js_behavior", {}).get("flags", [])
            for flag in js_flags:
                if flag.get("severity") in ("critical", "high"):
                    signals.add("obfuscation")
                if "crypto" in flag.get("name", "").lower():
                    signals.add("cryptomining")
                if "iframe" in flag.get("name", "").lower():
                    signals.add("iframe_injection")

            # Homograph/Typosquat
            if result_data.get("homograph", {}).get("is_homograph"):
                signals.add("homograph_attack")
            if result_data.get("typosquat", {}).get("is_typosquat"):
                signals.add("typosquatting")
            if result_data.get("brand_impersonation", {}).get("is_impersonation"):
                signals.add("brand_impersonation")

            # File specific
            if result_data.get("entropy", {}).get("classification") == "Packed/Encrypted":
                signals.add("packed_binary")
            if result_data.get("pe_metadata", {}).get("is_packed"):
                signals.add("packed_binary")
            if result_data.get("pe_metadata", {}).get("suspicious_imports"):
                signals.add("suspicious_api_calls")
            if result_data.get("macros", {}).get("suspicious"):
                signals.add("malicious_macro")

            # IP specific
            if result_data.get("tor", {}).get("is_tor"):
                signals.add("tor_usage")
            if result_data.get("vpn_proxy", {}).get("is_vpn"):
                signals.add("vpn_proxy")

            # Email specific
            if result_data.get("disposable", {}).get("is_disposable"):
                signals.add("disposable_email")
            auth = result_data.get("email_auth", {})
            if auth and auth.get("score", 100) < 50:
                signals.add("missing_email_auth")

            # QR specific
            if result_data.get("payment_qr", {}).get("is_suspicious"):
                signals.add("payment_fraud")

        # General phishing signals
        if "phish" in risk_level or "malicious" in risk_level:
            signals.add("phishing")

        return signals

    def analyze(self, scan_result: dict) -> dict[str, Any]:
        """Plugin interface."""
        return self.map_findings(scan_result)

    def health_check(self) -> dict[str, Any]:
        return {
            "module": "MITRE Mapper",
            "status": "Healthy",
            "techniques_loaded": len(self._techniques),
        }


mitre_mapper = MITREMapper()
