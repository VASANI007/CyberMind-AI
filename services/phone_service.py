"""
CyberMind AI
Phone Threat Intelligence & Scam Risk Service
Enterprise Production Version
"""

from __future__ import annotations

import re
from typing import Any
from core.logger import logger
from services.veriphone_service import veriphone_service
from services.ipqs_service import ipqs_service


COUNTRY_CODES = {
    "91": {"country": "India", "flag": "🇮🇳", "region": "South Asia"},
    "1": {"country": "United States / Canada", "flag": "🇺🇸/🇨🇦", "region": "North America"},
    "44": {"country": "United Kingdom", "flag": "🇬🇧", "region": "Europe"},
    "61": {"country": "Australia", "flag": "🇦🇺", "region": "Oceania"},
    "81": {"country": "Japan", "flag": "🇯🇵", "region": "East Asia"},
    "49": {"country": "Germany", "flag": "🇩🇪", "region": "Europe"},
    "33": {"country": "France", "flag": "🇫🇷", "region": "Europe"},
    "86": {"country": "China", "flag": "🇨🇳", "region": "East Asia"},
    "971": {"country": "United Arab Emirates", "flag": "🇦🇪", "region": "Middle East"},
    "92": {"country": "Pakistan", "flag": "🇵🇰", "region": "South Asia"},
    "880": {"country": "Bangladesh", "flag": "🇧🇩", "region": "South Asia"},
    "65": {"country": "Singapore", "flag": "🇸🇬", "region": "Southeast Asia"},
    "7": {"country": "Russia / Kazakhstan", "flag": "🇷🇺", "region": "Eurasia"},
    "55": {"country": "Brazil", "flag": "🇧🇷", "region": "South America"},
    "27": {"country": "South Africa", "flag": "🇿🇦", "region": "Africa"},
}


class PhoneService:
    """
    Phone Threat Intelligence Service.
    Parses telecom signals, queries Veriphone API & IPQS reputation intelligence, and evaluates scam risk.
    """

    def analyze(self, phone_number: str) -> dict[str, Any]:
        """
        Analyze a phone number for scam/fraud threat indicators.
        """
        clean = phone_number.strip()
        digits = re.sub(r"[^\d]", "", clean)
        
        # 1. Parse country code heuristics
        parsed_country = "Unknown / International"
        parsed_flag = "🌐"
        parsed_region = "Global"

        for code in sorted(COUNTRY_CODES.keys(), key=lambda k: len(k), reverse=True):
            if digits.startswith(code):
                parsed_country = COUNTRY_CODES[code]["country"]
                parsed_flag = COUNTRY_CODES[code]["flag"]
                parsed_region = COUNTRY_CODES[code]["region"]
                break

        # 2. Query Veriphone API for primary carrier & number validation
        veriphone_res = veriphone_service.validate_phone(clean)

        # 3. Query IPQS API for secondary threat intelligence
        ipqs_res = ipqs_service.validate_phone(clean)
        
        # 4. Combine Veriphone + IPQS + Heuristics
        veriphone_active = bool(veriphone_res.get("configured") and veriphone_res.get("success"))
        
        if veriphone_active:
            is_valid = veriphone_res.get("valid", True)
            country = veriphone_res.get("country") or parsed_country
            region = veriphone_res.get("region") or parsed_region
            carrier = veriphone_res.get("carrier") or "Telecom Provider Available"
            line_type = veriphone_res.get("line_type") or "Mobile"
        else:
            is_valid = ipqs_res.get("valid", True)
            country = ipqs_res.get("country") or parsed_country
            region = ipqs_res.get("region") or parsed_region
            carrier = ipqs_res.get("carrier") or "Telecom Provider Available"
            line_type = ipqs_res.get("line_type") or "Mobile"

        if country == "Not Available" or not country:
            country = f"{parsed_flag} {parsed_country}"
        elif parsed_flag not in country and parsed_country in country:
            country = f"{parsed_flag} {country}"

        city = ipqs_res.get("city") or "Not Available"
        
        prepaid_raw = ipqs_res.get("prepaid")
        prepaid = "Yes" if prepaid_raw is True else ("No" if prepaid_raw is False else "Not Available")
        
        voip = (line_type == "VoIP") or ipqs_res.get("voip", False)
        recent_abuse = ipqs_res.get("recent_abuse", False)
        fraud_score = ipqs_res.get("fraud_score", 0)
        spammer = ipqs_res.get("spammer", False)
        risky = ipqs_res.get("risky", False)
        leaked = ipqs_res.get("leaked", False)
        name = ipqs_res.get("name") or "Not Available"
        assoc_email = ipqs_res.get("associated_email") or "Not Available"

        reasons = []
        rule_score = fraud_score

        if veriphone_active:
            if not is_valid:
                rule_score += 35
                reasons.append("Unallocated or Invalid Number according to global telecom registry (Veriphone)")
            if line_type.lower() in ("voip", "virtual"):
                rule_score += 35
                reasons.append("VoIP / Virtual Number detected (Elevated Scam Risk)")
            elif line_type.lower() in ("toll free", "toll_free"):
                reasons.append("Toll-free / Business Number")
        else:
            if not ipqs_res.get("configured"):
                if line_type.lower() in ("voip", "non-fixed voip", "virtual"):
                    rule_score += 35
                    reasons.append("VoIP / Virtual Number detected")
                if digits.startswith("1800") or digits.startswith("1888"):
                    reasons.append("Toll-free / Business Number")

        if recent_abuse:
            reasons.append("Recent abuse & scam reports associated with number")
            rule_score = max(rule_score, 75)
        if voip and "VoIP" not in "".join(reasons):
            reasons.append("VoIP / Disposable Line Type")
            rule_score += 25
        if spammer:
            reasons.append("Known Robocaller / Spammer profile")
            rule_score += 30
        if risky:
            reasons.append("High-risk telecom reputation")
            rule_score += 20
        if leaked:
            reasons.append("Public leak / exposure record flag")
            rule_score += 15

        rule_score = min(rule_score, 100)

        # Verdict assignment
        if rule_score < 25:
            scam_risk = "Low"
            reputation = "Good"
            recommendation = "Safe — Standard phone number, no scam flags detected."
        elif rule_score < 60:
            scam_risk = "Medium"
            reputation = "Suspicious"
            recommendation = "Caution — Exercise care before sharing sensitive info or making payments."
        elif rule_score < 80:
            scam_risk = "High"
            reputation = "Risky"
            recommendation = "Avoid — Suspicious line attributes and elevated fraud risk detected."
        else:
            scam_risk = "Critical"
            reputation = "Highly Risky"
            recommendation = "Avoid Financial Interaction — Strong scam/fraud intelligence flagged."

        return {
            "target": clean,
            "valid": is_valid,
            "country": country,
            "region": region,
            "city": city,
            "carrier": carrier,
            "line_type": line_type,
            "prepaid": prepaid,
            "voip": "Yes" if voip else "No",
            "recent_abuse": "Yes" if recent_abuse else "No",
            "fraud_score": rule_score,
            "scam_risk": scam_risk,
            "reputation": reputation,
            "recommendation": recommendation,
            "public_identity": {
                "business_name": name,
                "exposure_leaked": "Yes" if leaked else "No",
                "associated_email": assoc_email
            },
            "reasons": reasons,
            "veriphone_integrated": veriphone_active,
            "ipqs_integrated": ipqs_res.get("configured", False),
            "veriphone_raw": veriphone_res,
            "raw": veriphone_res if veriphone_active else ipqs_res
        }

    def health_check(self) -> dict[str, Any]:
        """
        Health status.
        """
        return {
            "service": "Phone Service",
            "status": "Healthy"
        }


phone_service = PhoneService()
