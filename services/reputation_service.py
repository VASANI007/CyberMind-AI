"""
CyberMind AI

Reputation Service

Enterprise Production Version
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.logger import logger


class ReputationService:
    """
    Enterprise Reputation Engine.

    Responsibilities

    • Risk Scoring

    • Confidence Calculation

    • Threat Classification

    • Recommendation Engine

    • Decision Engine
    """

    MAX_SCORE = 100

    SCORE_WEIGHTS = {

        "blacklisted": 40,

        "google_safe_browsing": 30,

        "virustotal": 30,

        "young_domain": 15,

        "invalid_ssl": 10,

        "missing_security_headers": 10,

        "contains_ip": 10,

        "short_url": 10,

        "punycode": 15,

        "brand_impersonation": 20,

        "suspicious_keywords": 10,

        "high_entropy": 5,

        "multiple_subdomains": 5,

        "suspicious_extension": 10,

        "multiple_redirects": 10

    }

    RISK_LEVELS = {

        (0, 20): "Safe",

        (21, 40): "Low",

        (41, 60): "Medium",

        (61, 80): "High",

        (81, 100): "Critical"

    }

    RECOMMENDATIONS = {

        "Safe":

            "No significant threats detected.",

        "Low":

            "Exercise caution before visiting.",

        "Medium":

            "Proceed carefully and verify website legitimacy.",

        "High":

            "Avoid entering sensitive information.",

        "Critical":

            "Do not visit this website."

    }

    def __init__(self) -> None:
        self.popular_domains: set[str] = set()
        self._load_popular_domains()
        logger.info(
            "Reputation Service initialized."
        )

    def _load_popular_domains(self) -> None:
        try:
            pop_path = Path(__file__).parent.parent / "data" / "domain" / "popular_domains.json"
            if pop_path.exists():
                with open(pop_path, "r", encoding="utf-8") as f:
                    domains = json.load(f)
                    if isinstance(domains, list):
                        self.popular_domains = set(d.lower().strip() for d in domains if isinstance(d, str))
        except Exception as exc:
            logger.warning("Could not load popular_domains.json in reputation service: %s", exc)

    def _extract_domain(self, report: dict[str, Any]) -> str:
        domain = report.get("domain")
        if isinstance(domain, dict):
            domain = domain.get("domain") or domain.get("name")
        if not domain:
            url = report.get("url") or report.get("target") or ""
            if "://" in url:
                domain = url.split("://")[1].split("/")[0].split(":")[0]
            elif "/" in url:
                domain = url.split("/")[0].split(":")[0]
            else:
                domain = url
        dom = str(domain or "").lower().strip()
        if dom.startswith("www."):
            dom = dom[4:]
        return dom

    def _is_popular_domain(self, report: dict[str, Any]) -> bool:
        dom = self._extract_domain(report)
        if not dom:
            return False
        for pop in self.popular_domains:
            if dom == pop or dom.endswith("." + pop):
                return True
        return False

    def _limit_score(

        self,

        score: int

    ) -> int:
        """
        Clamp score.
        """

        return max(

            0,

            min(

                score,

                self.MAX_SCORE

            )

        )

    def _feature(

        self,

        report: dict[str, Any],

        key: str,

        default: Any = None

    ) -> Any:
        """
        Feature helper.
        """

        features = report.get("features")
        if not features and "url_analysis" in report:
            features = report.get("url_analysis", {}).get("features")

        return (features or {}).get(key, default)

    def _section(

        self,

        report: dict[str, Any],

        name: str

    ) -> dict[str, Any]:
        """
        Section helper.
        """

        section = report.get(name)
        if not section and "url_analysis" in report:
            section = report.get("url_analysis", {}).get(name)

        return section or {}

    def _bool(

        self,

        value: Any

    ) -> bool:

        return bool(

            value

        )

    def _int(

        self,

        value: Any

    ) -> int:

        try:

            return int(

                value

            )

        except Exception:

            return 0

    def _float(

        self,

        value: Any

    ) -> float:

        try:

            return float(

                value

            )

        except Exception:

            return 0.0
        

    def feature_score(
        self,
        report: dict[str, Any]
    ) -> tuple[int, list[str]]:
        """
        Calculate score using
        URL lexical features.
        """

        score = 0

        reasons = []

        if self._bool(

            self._feature(

                report,

                "contains_ip"

            )

        ):

            score += self.SCORE_WEIGHTS[

                "contains_ip"

            ]

            reasons.append(

                "URL contains IP address."

            )

        if self._bool(

            self._feature(

                report,

                "contains_punycode"

            )

        ):

            score += self.SCORE_WEIGHTS[

                "punycode"

            ]

            reasons.append(

                "Punycode detected."

            )

        if self._bool(

            self._feature(

                report,

                "short_url"

            )

        ):

            score += self.SCORE_WEIGHTS[

                "short_url"

            ]

            reasons.append(

                "Shortened URL detected."

            )

        if self._bool(

            self._feature(

                report,

                "contains_brand_name"

            )

        ):

            score += self.SCORE_WEIGHTS[

                "brand_impersonation"

            ]

            reasons.append(

                "Brand name detected."

            )

        keyword_count = self._int(

            self._feature(

                report,

                "keyword_count"

            )

        )

        if keyword_count > 0:

            score += min(

                keyword_count * 2,

                self.SCORE_WEIGHTS[

                    "suspicious_keywords"

                ]

            )

            reasons.append(

                f"{keyword_count} suspicious keyword(s)."

            )

        entropy = self._float(

            self._feature(

                report,

                "url_entropy"

            )

        )

        if entropy >= 4.5:

            score += self.SCORE_WEIGHTS[

                "high_entropy"

            ]

            reasons.append(

                "High URL entropy."

            )

        subdomains = self._int(

            self._feature(

                report,

                "subdomain_count"

            )

        )

        if subdomains >= 3:

            score += self.SCORE_WEIGHTS[

                "multiple_subdomains"

            ]

            reasons.append(

                "Multiple subdomains."

            )

        if self._bool(

            self._feature(

                report,

                "suspicious_extension"

            )

        ):

            score += self.SCORE_WEIGHTS[

                "suspicious_extension"

            ]

            reasons.append(

                "Suspicious file extension."

            )

        score = self._limit_score(

            score

        )

        return (

            score,

            reasons

        )


    def intelligence_score(
        self,
        report: dict[str, Any]
    ) -> tuple[int, list[str]]:
        """
        Calculate score using
        external intelligence.
        """

        score = 0

        reasons = []

        blacklist = self._section(

            report,

            "blacklist"

        )

        if self._bool(

            blacklist.get(

                "detected",

                False

            )

        ) or self._bool(

            blacklist.get(

                "blacklisted",

                False

            )

        ):

            score += self.SCORE_WEIGHTS[

                "blacklisted"

            ]

            reasons.append(

                "URL found in blacklist."

            )

        google = self._section(

            report,

            "google_safe_browsing"

        )

        if self._bool(

            google.get(

                "malicious",

                False

            )

        ) or (

            "safe" in google and not self._bool(google.get("safe", True))

        ):

            score += self.SCORE_WEIGHTS[

                "google_safe_browsing"

            ]

            reasons.append(

                "Detected by Google Safe Browsing."

            )

        virustotal = self._section(

            report,

            "virustotal"

        )

        malicious = self._int(

            virustotal.get(

                "malicious",

                0

            )

        )

        if malicious > 0:
            if malicious == 1:
                score += 5
                reasons.append("VirusTotal single engine detection (possible false positive).")
            elif malicious == 2:
                score += 12
                reasons.append(f"VirusTotal detected {malicious} engine(s).")
            else:
                score += self.SCORE_WEIGHTS[
                    "virustotal"
                ]
                reasons.append(
                    f"VirusTotal detected {malicious} engine(s)."
                )

        ssl = self._section(

            report,

            "ssl"

        )

        if not self._bool(

            ssl.get(

                "valid",

                True

            )

        ):

            score += self.SCORE_WEIGHTS[

                "invalid_ssl"

            ]

            reasons.append(

                "Invalid SSL certificate."

            )

        headers = self._section(

            report,

            "security_headers"

        )

        header_score = self._int(

            headers.get(

                "score",

                100

            )

        )

        if header_score < 50:

            score += self.SCORE_WEIGHTS[

                "missing_security_headers"

            ]

            reasons.append(

                "Weak security headers."

            )

        whois = self._section(

            report,

            "whois"

        )

        age = self._int(

            whois.get(

                "domain_age_days"

            )

            if whois.get("domain_age_days") is not None

            else whois.get("age_days", 365)

        )

        if age < 30:

            score += self.SCORE_WEIGHTS[

                "young_domain"

            ]

            reasons.append(

                "Recently registered domain."

            )

        abuseipdb = self._section(

            report,

            "abuseipdb"

        )

        abuse_score = self._int(

            abuseipdb.get(

                "risk_score",

                0

            )

        )

        if abuse_score > 0:

            score += int(abuse_score * 0.5)

            reasons.append(

                f"AbuseIPDB abuse score: {abuse_score}%."

            )

        score = self._limit_score(

            score

        )

        return (

            score,

            reasons

        )
        

    def calculate_score(
        self,
        report: dict[str, Any]
    ) -> tuple[int, list[str]]:
        """
        Calculate final reputation score.
        """

        feature_score, feature_reasons = (

            self.feature_score(
                report
            )

        )

        intelligence_score, intelligence_reasons = (

            self.intelligence_score(
                report
            )

        )

        total_score = (
            feature_score
            +
            intelligence_score
        )

        # Popular domains protection: if known authentic domain with clean hard threat intel, cap risk score
        is_pop = self._is_popular_domain(report)
        blacklist = self._section(report, "blacklist")
        google = self._section(report, "google_safe_browsing")
        has_hard_threat = (
            bool(blacklist.get("detected") or blacklist.get("blacklisted"))
            or bool(google.get("malicious"))
            or (self._int(self._section(report, "virustotal").get("malicious", 0)) >= 3)
        )
        if is_pop and not has_hard_threat:
            total_score = min(total_score, 5)

        total_score = self._limit_score(
            total_score
        )

        reasons = (

            feature_reasons

            +

            intelligence_reasons

        )

        return (

            total_score,

            reasons

        )

    def confidence(
        self,
        report: dict[str, Any]
    ) -> float:
        """
        Calculate confidence score.
        """

        available = 0

        sections = [

            "features",

            "dns",

            "whois",

            "ssl",

            "security_headers",

            "blacklist",

            "google_safe_browsing",

            "virustotal"

        ]

        for section in sections:

            if report.get(

                section

            ):

                available += 1

        return round(

            (

                available

                /

                len(sections)

            )

            *

            100,

            2

        )

    def risk_level(
        self,
        score: int
    ) -> str:
        """
        Return risk level.
        """

        for (

            minimum,

            maximum

        ), level in self.RISK_LEVELS.items():

            if minimum <= score <= maximum:

                return level

        return "Unknown"

    def recommendation(
        self,
        level: str
    ) -> str:
        """
        Return recommendation.
        """

        return self.RECOMMENDATIONS.get(

            level,

            "Unknown."

        )

    def safe(
        self,
        score: int
    ) -> bool:
        """
        Safe or not.
        """

        return score <= 20
    

    def analyze(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyze report and return
        final reputation.
        """

        logger.info(

            "Calculating reputation."

        )

        score, reasons = (

            self.calculate_score(

                report

            )

        )

        level = self.risk_level(

            score

        )

        confidence = self.confidence(

            report

        )

        recommendation = (

            self.recommendation(

                level

            )

        )

        return {

            "risk_score": score,

            "score": 100 - score,

            "risk_level": level,

            "confidence": confidence,

            "safe": self.safe(

                score

            ),

            "recommendation": recommendation,

            "reasons": reasons

        }

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Service health.
        """

        return {

            "service":

                "Reputation Service",

            "status":

                "Healthy",

            "max_score":

                self.MAX_SCORE,

            "rules":

                len(

                    self.SCORE_WEIGHTS

                )

        }

    def __repr__(
        self
    ) -> str:

        return (

            "ReputationService("

            "Enterprise Version)"

        )


reputation_service = ReputationService()