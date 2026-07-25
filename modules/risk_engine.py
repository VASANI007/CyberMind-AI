"""
CyberMind AI

Risk Engine

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger


class RiskEngine:
    """
    Enterprise Risk Engine.

    Responsibilities

    • Risk Score

    • Risk Level

    • Confidence

    • Threat Indicators

    • Final Decision
    """

    UNVERIFIED = "Unverified"
    SAFE = "Safe"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

    def __init__(
        self
    ) -> None:

        logger.info(

            "Risk Engine initialized."

        )

    def calculate(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Calculate overall risk.
        
        Section 16 — Fail-open logic:
        • Track which data sources actually returned results vs. defaulted to empty.
        • data_completeness = % of sources that returned real data.
        • confidence is now based on data availability, NOT inverse of score.
        • Missing data is a mild risk signal (unverifiable target).
        """

        score = 0
        reasons = []

        # ── Source tracking for data_completeness ──
        expected_sources = [
            "reputation", "blacklist", "ssl", "google_safe_browsing", "virustotal"
        ]
        sources_present = 0

        reputation = report.get("reputation", {})
        if reputation:
            sources_present += 1

        blacklist = report.get("blacklist", {})
        if not blacklist and "url_analysis" in report:
            blacklist = report["url_analysis"].get("blacklist", {})
        if blacklist:
            sources_present += 1

        ssl = report.get("ssl", {})
        if not ssl and "url_analysis" in report:
            ssl = report["url_analysis"].get("ssl", {})
        if ssl:
            sources_present += 1

        google = report.get("google_safe_browsing", {})
        if not google and "url_analysis" in report:
            google = report["url_analysis"].get("google_safe_browsing", {})
        if google:
            sources_present += 1

        virustotal = report.get("virustotal", {})
        if not virustotal and "url_analysis" in report:
            virustotal = report["url_analysis"].get("virustotal", {})
        if virustotal:
            sources_present += 1

        data_completeness = round(
            (sources_present / len(expected_sources)) * 100, 1
        ) if expected_sources else 100.0

        # ── Fail-open: missing data = mild risk signal ──
        missing_count = len(expected_sources) - sources_present
        if missing_count >= 3:
            score += 15
            reasons.append(f"Low data completeness ({sources_present}/{len(expected_sources)} sources)")
        elif missing_count >= 2:
            score += 8
            reasons.append(f"Partial data ({sources_present}/{len(expected_sources)} sources)")

        # Reputation
        reputation_score = reputation.get("score", 100)

        if reputation_score < 80:
            score += 10
            reasons.append("Low reputation score")
        if reputation_score < 60:
            score += 20
        if reputation_score < 40:
            score += 20

        # Blacklist
        if blacklist.get("detected", False) or blacklist.get("blacklisted", False):
            score += 40
            reasons.append("Blacklisted")

        # SSL
        if not ssl.get("valid", True):
            score += 15
            reasons.append("Invalid SSL")

        # Google Safe Browsing
        if google.get("malicious", False) or (
            "safe" in google and not google.get("safe", True)
        ):
            score += 50
            reasons.append("Google Safe Browsing")

        # VirusTotal
        malicious = virustotal.get("malicious", 0)
        if malicious > 0:
            score += malicious * 5
            reasons.append("VirusTotal detection")

        # Homograph / Typosquat / Brand Impersonation
        if report.get("homograph", {}).get("is_homograph"):
            score += 25
            reasons.append("Homograph Unicode attack")
        if report.get("typosquat", {}).get("is_typosquat"):
            score += 20
            reasons.append("Typosquatting domain")
        if report.get("brand_impersonation", {}).get("is_impersonation"):
            score += 30
            reasons.append("Brand impersonation detected")

        # TOR / VPN
        if report.get("tor", {}).get("is_tor"):
            score += 35
            reasons.append("TOR Exit Node IP")
        if report.get("vpn_proxy", {}).get("is_vpn"):
            score += 15
            reasons.append("VPN / Proxy IP")

        # Disposable email
        if report.get("disposable", {}).get("is_disposable"):
            score += 25
            reasons.append("Disposable / temporary email domain")

        # File entropy & Macros
        # File entropy & Macros
        if report.get("entropy_analysis", {}).get("is_suspicious"):
            score += report.get("entropy_analysis", {}).get("risk_contribution", 15)
            reasons.append("Suspicious file entropy")
        if report.get("macro_detection", {}).get("suspicious"):
            score += report.get("macro_detection", {}).get("risk_contribution", 25)
            reasons.append("Suspicious Office VBA macro")

        # Lexical suspicious keywords check
        keyword_check = report.get("lexical_keywords", {})
        if not keyword_check and "url_analysis" in report:
            keyword_check = report["url_analysis"].get("lexical_keywords", {})
        if not keyword_check and "analysis" in report:
            keyword_check = report["analysis"].get("lexical_keywords", {})

        if keyword_check.get("severity") == "high":
            score += 35
            matched_kws = keyword_check.get("matched_keywords", [])
            reasons.append(f"Alarming keyword(s) found in target: {', '.join(matched_kws)}")
        elif keyword_check.get("severity") == "medium":
            score += 15
            matched_kws = keyword_check.get("matched_keywords", [])
            reasons.append(f"Suspicious keyword(s) found in target: {', '.join(matched_kws)}")

        score = min(score, 100)

        breakdown = {
            "reputation_weight": 20 if reputation_score < 80 else 0,
            "blacklist_weight": 40 if (blacklist.get("detected") or blacklist.get("blacklisted")) else 0,
            "ssl_weight": 15 if not ssl.get("valid", True) else 0,
            "threat_intel_weight": 50 if google.get("malicious") else min(malicious * 5, 50),
            "heuristic_weight": min(score, 100)
        }

        # Calculate cross-API consensus score
        consensus = self.consensus_score(report)

        # ── Decoupled confidence (based on data availability, NOT score) ──
        base_confidence = data_completeness  # 0-100
        if consensus["sources_checked"] > 0:
            agreement_bonus = consensus["consensus_ratio"] * 15  # up to +15
            base_confidence = min(100.0, base_confidence + agreement_bonus)
        confidence = round(base_confidence, 1)

        return {
            "score": score,
            "level": self.level(score, data_completeness),
            "confidence": confidence,
            "data_completeness": data_completeness,
            "sources_present": sources_present,
            "sources_expected": len(expected_sources),
            "reasons": reasons,
            "breakdown": breakdown,
            "consensus": consensus
        }

    def consensus_score(self, report: dict[str, Any]) -> dict[str, Any]:
        """
        Calculates agreement across multiple threat intelligence sources.
        """
        sources_checked = 0
        sources_flagged = 0

        # Source 1: Google Safe Browsing
        google = report.get("google_safe_browsing", {})
        if google:
            sources_checked += 1
            if google.get("malicious") or not google.get("safe", True):
                sources_flagged += 1

        # Source 2: VirusTotal
        vt = report.get("virustotal", {})
        if vt:
            sources_checked += 1
            if vt.get("malicious", 0) > 0:
                sources_flagged += 1

        # Source 3: Blacklist Service
        bl = report.get("blacklist", {})
        if bl:
            sources_checked += 1
            if bl.get("blacklisted") or bl.get("detected"):
                sources_flagged += 1

        # Source 4: AbuseIPDB
        abuse = report.get("abuseipdb", {})
        if abuse:
            sources_checked += 1
            if abuse.get("abuse_score", 0) > 25:
                sources_flagged += 1

        ratio = (sources_flagged / sources_checked) if sources_checked > 0 else 0.0
        return {
            "sources_checked": sources_checked,
            "sources_flagged": sources_flagged,
            "consensus_ratio": round(ratio, 2),
            "summary": f"{sources_flagged}/{sources_checked} sources flagged threat" if sources_checked > 0 else "No sources available"
        }

    def level(
        self,
        score: int,
        data_completeness: float = 100.0
    ) -> str:
        """
        Risk level computation considering score & data completeness.
        """
        if score < 20:
            if data_completeness < 50:
                return self.UNVERIFIED
            return self.SAFE
        if score < 40:
            return self.LOW
        if score < 60:
            return self.MEDIUM
        if score < 80:
            return self.HIGH
        return self.CRITICAL

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Engine health.
        """
        return {
            "service": "Risk Engine",
            "status": "Healthy",
            "version": "2.0"
        }

    def supported_levels(
        self
    ) -> list[str]:
        """
        Supported risk levels.
        """
        return [
            self.UNVERIFIED,
            self.SAFE,
            self.LOW,
            self.MEDIUM,
            self.HIGH,
            self.CRITICAL
        ]

    def __repr__(
        self
    ) -> str:

        return (

            "RiskEngine("

            "Enterprise Version)"

        )


risk_engine = RiskEngine()