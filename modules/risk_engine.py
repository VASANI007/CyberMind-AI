"""
CyberMind AI

Risk Engine

Enterprise Production Version
"""

from __future__ import annotations

import json
from pathlib import Path
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
        self.popular_domains: set[str] = set()
        self._load_popular_domains()
        logger.info(
            "Risk Engine initialized."
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
            logger.warning("Could not load popular_domains.json in risk engine: %s", exc)

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

        def _extract(key):
            v = report.get(key)
            if not v and "url_analysis" in report:
                v = report["url_analysis"].get(key)
            if not v and "analysis" in report:
                v = report["analysis"].get(key)
            if not v and "domain_data" in report:
                v = report["domain_data"].get(key)
            if not v and "url_data" in report:
                v = report["url_data"].get(key)
            if isinstance(v, dict):
                return v
            elif isinstance(v, str):
                return {"value": v, "score": 100 if v in ("Good", "Excellent") else (50 if v == "Suspicious" else 20)}
            return {}


        reputation = _extract("reputation")
        if reputation:
            sources_present += 1

        blacklist = _extract("blacklist")
        if blacklist:
            sources_present += 1

        ssl = _extract("ssl")
        if ssl:
            sources_present += 1

        google = _extract("google_safe_browsing")
        if google:
            sources_present += 1

        virustotal = _extract("virustotal")
        if virustotal:
            sources_present += 1

        data_completeness = round(
            (sources_present / len(expected_sources)) * 100, 1
        ) if expected_sources else 100.0

        missing_count = len(expected_sources) - sources_present

        # Extract sub-sections for granular calculations
        whois = _extract("whois")
        sec_headers = _extract("security_headers")
        features_data = _extract("features")

        # 1. Google Safe Browsing (Live Threat Feed)
        if google.get("malicious", False) or (
            "safe" in google and not google.get("safe", True)
        ):
            score += 65.0
            reasons.append("Google Safe Browsing Flagged Malicious")

        # 2. Blacklist (Threat Databases)
        if blacklist.get("detected", False) or blacklist.get("blacklisted", False):
            score += 55.0
            reasons.append("Blacklisted across threat databases")

        # 3. VirusTotal (Continuous Ratio of live engines)
        malicious = virustotal.get("malicious", 0)
        vt_stats = virustotal.get("stats") or virustotal.get("risk") or {}
        total_engines = vt_stats.get("harmless", 0) + vt_stats.get("malicious", 0) + vt_stats.get("suspicious", 0)
        if total_engines <= 0:
            total_engines = 88
        if malicious > 0:
            if malicious == 1:
                score += 2.0
                reasons.append("VirusTotal: 1 engine flag (heuristic anomaly)")
            elif malicious == 2:
                score += 5.5
                reasons.append(f"VirusTotal detected {malicious} engine flags")
            else:
                vt_ratio = malicious / total_engines
                vt_pts = round(18.0 + min(50.0, vt_ratio * 95.0), 1)
                score += vt_pts
                reasons.append(f"VirusTotal detected {malicious} engine flags (+{int(vt_pts)} pts)")

        # 4. SSL Analysis (Live TLS Handshake)
        if not ssl.get("valid", True):
            score += 14.0
            reasons.append("Invalid or missing SSL certificate")

        # 5. WHOIS Domain Age (Continuous Curve)
        domain_age = whois.get("domain_age_days")
        if domain_age is not None:
            try:
                age_days = float(domain_age)
                if age_days < 30:
                    age_pen = round(13.0 * (1.0 - (age_days / 30.0)), 1)
                    score += age_pen
                    reasons.append(f"Newly registered domain ({int(age_days)} days old)")
                elif age_days < 180:
                    age_pen = round(6.0 * (1.0 - ((age_days - 30) / 150.0)), 1)
                    score += age_pen
                elif age_days > 1825:
                    trust_credit = min(5.0, round((age_days - 1825) / 1500.0, 1))
                    score = max(0.0, score - trust_credit)
            except Exception:
                pass

        # 6. Security Headers (Continuous floating score)
        header_score = sec_headers.get("score")
        if header_score is not None:
            try:
                h_val = float(header_score)
                if h_val < 50:
                    h_pen = round((50.0 - h_val) * 0.08, 1)
                    score += h_pen
            except Exception:
                pass

        # 7. URL Shannon Entropy (Continuous Float)
        url_entropy = features_data.get("url_entropy")
        if url_entropy is not None:
            try:
                e_val = float(url_entropy)
                if e_val > 4.2:
                    ent_pen = round(min(11.0, (e_val - 4.2) * 8.5), 1)
                    score += ent_pen
                    reasons.append(f"Suspicious URL entropy ({e_val:.2f})")
            except Exception:
                pass

        # 8. Homograph / Typosquat / Brand Impersonation
        homograph_data = _extract("homograph")
        if homograph_data.get("is_homograph"):
            score += 38.0
            reasons.append("Homograph Unicode attack")

        typosquat_data = _extract("typosquat")
        if typosquat_data.get("is_typosquat"):
            score += 29.0
            reasons.append("Typosquatting domain")

        brand_data = _extract("brand_impersonation")
        if brand_data.get("is_impersonation"):
            score += 41.0
            reasons.append("Brand impersonation detected")

        # 9. TOR / VPN / Disposable
        tor_data = _extract("tor")
        if tor_data.get("is_tor"):
            score += 48.0
            reasons.append("TOR Exit Node IP")

        vpn_data = _extract("vpn_proxy")
        if vpn_data.get("is_vpn"):
            score += 16.0
            reasons.append("VPN / Proxy IP")

        disposable_data = _extract("disposable")
        if disposable_data.get("is_disposable"):
            score += 37.0
            reasons.append("Disposable / temporary email domain")

        # 10. File Entropy & Macros
        entropy_data = _extract("entropy_analysis")
        if entropy_data.get("is_suspicious"):
            score += float(entropy_data.get("risk_contribution", 22))
            reasons.append("Suspicious file entropy")

        macro_data = _extract("macro_detection")
        if macro_data.get("suspicious"):
            score += float(macro_data.get("risk_contribution", 31))
            reasons.append("Suspicious Office VBA macro")

        # 11. Lexical Suspicious Keywords
        keyword_check = _extract("lexical_keywords")
        if keyword_check.get("severity") == "high":
            score += 54.0
            matched_kws = keyword_check.get("matched_keywords", [])
            reasons.append(f"Alarming keyword(s) found in target: {', '.join(matched_kws)}")
        elif keyword_check.get("severity") == "medium":
            score += 19.0
            matched_kws = keyword_check.get("matched_keywords", [])
            reasons.append(f"Suspicious keyword(s) found in target: {', '.join(matched_kws)}")

        # 12. Phone Threat Intelligence
        if report.get("line_type") and report.get("scam_risk"):
            phone_fraud = report.get("fraud_score", 0)
            if phone_fraud > 0:
                score = max(score, float(phone_fraud))
            if report.get("recent_abuse") == "Yes":
                reasons.append("Phone number associated with recent abuse/scam reports")
            if report.get("voip") == "Yes":
                score += 18.0
                reasons.append("VoIP / Virtual Phone Line (High Risk)")

        # Target domain extraction for trusted domain checks
        dom_val = (
            report.get("domain")
            or report.get("domain_name")
            or report.get("target")
            or report.get("url")
            or report.get("hostname")
            or ""
        )
        if isinstance(dom_val, dict):
            dom_val = dom_val.get("domain") or dom_val.get("name") or ""
        dom_str = str(dom_val).lower().strip()
        if "://" in dom_str:
            dom_str = dom_str.split("://")[1].split("/")[0].split(":")[0]
        elif "/" in dom_str:
            dom_str = dom_str.split("/")[0].split(":")[0]
        if ":" in dom_str:
            dom_str = dom_str.split(":")[0]
        if dom_str.startswith("www."):
            dom_str = dom_str[4:]

        is_trusted_popular = False
        if dom_str and self.popular_domains:
            for pop in self.popular_domains:
                if dom_str == pop or dom_str.endswith("." + pop):
                    is_trusted_popular = True
                    break

        has_verified_threat = (
            bool(blacklist.get("detected") or blacklist.get("blacklisted"))
            or bool(google.get("malicious") or ("safe" in google and not google.get("safe", True)))
            or malicious >= 3
        )

        # 13. AI / ML Prediction Integration (Continuous Probability)
        ml_data = _extract("ml_prediction")
        if not ml_data and "ml_prediction" in report:
            ml_data = report.get("ml_prediction") or {}
        
        ml_pred_name = str(ml_data.get("prediction", "")).strip().lower()
        ml_conf_val = ml_data.get("confidence")
        if ml_conf_val is None:
            ml_conf_val = ml_data.get("probability")
        try:
            ml_conf_float = float(ml_conf_val) if ml_conf_val is not None else 0.0
        except Exception:
            ml_conf_float = 0.0

        has_major_signals = (
            has_verified_threat
            or (keyword_check.get("severity") == "high")
            or bool(homograph_data.get("is_homograph"))
            or bool(brand_data.get("is_impersonation"))
            or bool(typosquat_data.get("is_typosquat"))
        )

        prob_0_1 = ml_conf_float if ml_conf_float <= 1.0 else ml_conf_float / 100.0

        if ml_pred_name in ("phishing", "malicious", "threat") and prob_0_1 >= 0.60:
            ai_risk_weight = round(prob_0_1 * 34.0, 1)
            score += ai_risk_weight
            reasons.append(f"AI Phishing model flagged target ({prob_0_1:.1%} confidence)")
        elif ml_pred_name in ("legitimate", "safe", "clean", "benign") and prob_0_1 >= 0.70:
            if not has_major_signals:
                ai_discount = round(prob_0_1 * 11.5, 1)
                score = max(0.0, score - ai_discount)

        # 14. Reputation Service (Continuous Deviation)
        reputation_score = reputation.get("score")
        if reputation_score is not None:
            try:
                rep_val = float(reputation_score)
                if rep_val < 80.0:
                    rep_pen = round((80.0 - rep_val) * 0.32, 1)
                    score += rep_pen
                    if rep_pen >= 7.0:
                        reasons.append(f"Low reputation score ({int(rep_val)}/100)")
            except Exception:
                pass

        # 15. Trusted Popular Domain Trust Credit (Natural continuous credit)
        if is_trusted_popular and not has_major_signals:
            score = max(0.0, score - 7.0)
            reasons = [
                r for r in reasons
                if not (
                    "Low reputation" in r or "VirusTotal" in r or "keyword" in r.lower()
                    or "data completeness" in r.lower() or "Partial data" in r
                )
            ]
            reasons.append(f"Verified authentic popular domain ({dom_str})")

        # Fail-open / data completeness
        if missing_count >= 3:
            score += 11.0
            reasons.append(f"Low data completeness ({sources_present}/{len(expected_sources)} sources)")
        elif missing_count >= 2:
            score += 6.0
            reasons.append(f"Partial data ({sources_present}/{len(expected_sources)} sources)")

        score = int(round(min(100.0, max(0.0, score))))


        rep_val_breakdown = reputation.get("score")
        if rep_val_breakdown is None:
            rep_val_breakdown = 100

        breakdown = {
            "reputation_weight": 20 if rep_val_breakdown < 80 else 0,
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