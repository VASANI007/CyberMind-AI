"""
CyberMind AI
Universal Scan Module
"""

from __future__ import annotations

import time
import re
from typing import Any

from core.logger import logger
from services.url_service import url_service
from services.website_service import website_service
from services.domain_service import domain_service
from services.email_service import email_service
from services.ssl_service import ssl_service
from services.whois_service import whois_service
from services.dns_service import dns_service
from services.breach_intelligence_service import breach_intelligence_service
from services.device_security_service import device_security_service
from modules.risk_engine import risk_engine
from database.db import db

class UniversalScanModule:
    """
    Universal Scan coordinator that automatically classifies input
    and triggers multiple specialized backend scanner checks.
    """

    def __init__(self) -> None:
        logger.info("Universal Scan Module initialized.")

    def classify_input(self, val: str) -> str:
        """
        Classifies input string into 'email', 'url', or 'domain'.
        """
        val_clean = val.strip().lower()
        if "@" in val_clean:
            return "email"
        elif val_clean.startswith("http://") or val_clean.startswith("https://") or "/" in val_clean:
            return "url"
        else:
            return "domain"

    def analyze(self, value: str) -> dict[str, Any]:
        """
        Classifies input and runs the corresponding multi-module scan.
        """
        logger.info(f"Universal Scan triggered for: {value}")
        start_time = time.time()
        
        input_type = self.classify_input(value)
        
        risk_score = 0
        risk_level = "Safe"
        details = {}
        
        if input_type == "email":
            # 1. Email validation
            is_valid = email_service.validate(value)
            
            # 2. MX Record
            mx_avail = False
            mx_records = []
            try:
                dns_rep = email_service.dns(value)
                mx_records = dns_rep.get("mx_records", [])
                mx_avail = len(mx_records) > 0
            except Exception:
                pass
                
            # 3. Disposable Check
            is_disposable = False
            domain = value.strip().lower().split("@")[-1] if "@" in value else ""
            try:
                chk = device_security_service.check_email_security(value)
                is_disposable = chk.get("disposable", False)
            except Exception:
                pass
                
            # 4. Data Breach Check
            breach_found = False
            breaches_count = 0
            records_lost = 0
            breach_details = ""
            try:
                breach_rep = breach_intelligence_service.get_breach_report(domain)
                if breach_rep:
                    breach_found = True
                    breaches_count = breach_rep.get("total_breaches", 0)
                    records_lost = breach_rep.get("total_records", 0)
                    breach_details = breach_rep.get("ai_summary", "")
            except Exception:
                pass
                
            # Compute Risk
            if is_disposable:
                risk_score = 80
                risk_level = "High"
            elif breach_found:
                risk_score = 45
                risk_level = "Medium"
            elif not is_valid or not mx_avail:
                risk_score = 65
                risk_level = "High"
            else:
                risk_score = 8
                risk_level = "Safe"
                
            # AI Recommendation
            recs = ["Ensure email domain is valid and hosts active MX servers."]
            if is_disposable:
                recs.append("Avoid registering critical corporate accounts with temporary or disposable email addresses.")
            if breach_found:
                recs.append("Change all passwords on compromised accounts immediately and enable MFA (Multi-Factor Authentication).")
            else:
                recs.append("Email appears safe. Monitor regular checkups.")
                
            details = {
                "input_type": "email",
                "email": value,
                "domain": domain,
                "is_valid": is_valid,
                "mx_available": mx_avail,
                "mx_records": mx_records,
                "is_disposable": is_disposable,
                "breach_found": breach_found,
                "breach_count": breaches_count,
                "records_lost": records_lost,
                "breach_details": breach_details,
                "recommendations": recs
            }
            
        elif input_type == "url":
            # 1. URL scanner
            url_res = {}
            try:
                url_res = url_service.analyze(value)
            except Exception:
                pass
                
            # 2. Website scanner
            web_res = {}
            try:
                web_res = website_service.analyze(value)
            except Exception:
                pass
                
            # 3. SSL analysis
            ssl_valid = False
            ssl_issuer = "Unknown"
            try:
                domain_only = value.split("://")[-1].split("/")[0]
                ssl_res = ssl_service.analyze(domain_only)
                ssl_valid = ssl_res.get("valid", False)
                ssl_issuer = ssl_res.get("issuer", "Unknown")
            except Exception:
                pass
                
            # 4. Redirect & Phishing
            redirect_count = url_res.get("redirect_count", 0)
            is_malicious = url_res.get("google_safe_browsing", {}).get("malicious", False) or \
                           url_res.get("virustotal", {}).get("malicious", 0) > 0
                           
            # Risk logic (using risk engine check on url results)
            calc_risk = risk_engine.calculate(url_res)
            risk_score = calc_risk.get("score", 15)
            risk_level = calc_risk.get("level", "Safe")
            
            recs = ["Ensure the site enforces HTTPS connection globally."]
            if is_malicious:
                recs.append("Avoid interacting with this domain. It is flagged as unsafe/malicious by threat vendors.")
            if not ssl_valid:
                recs.append("Install a valid SSL/TLS certificate to secure connection transfers.")
                
            details = {
                "input_type": "url",
                "url": value,
                "ssl_valid": ssl_valid,
                "ssl_issuer": ssl_issuer,
                "redirect_count": redirect_count,
                "is_malicious": is_malicious,
                "recommendations": recs,
                "url_data": url_res,
                "website_data": web_res
            }
            
        else: # domain
            # 1. Domain scan
            dom_res = {}
            try:
                dom_res = domain_service.analyze(value)
            except Exception:
                pass
                
            # 2. Website scan
            web_res = {}
            try:
                web_res = website_service.analyze(f"http://{value}")
            except Exception:
                pass
                
            # 3. SSL Check
            ssl_valid = False
            ssl_issuer = "Unknown"
            try:
                ssl_res = ssl_service.analyze(value)
                ssl_valid = ssl_res.get("valid", False)
                ssl_issuer = ssl_res.get("issuer", "Unknown")
            except Exception:
                pass
                
            # 4. WHOIS
            registrar = "Unknown"
            created_date = "Unknown"
            try:
                whois_res = whois_service.analyze(value)
                registrar = whois_res.get("registrar", "Unknown")
                created_date = whois_res.get("creation_date", "Unknown")
            except Exception:
                pass
                
            # 5. DNS check
            ips = []
            try:
                dns_res = dns_service.analyze(value)
                ips = dns_res.get("ips", [])
            except Exception:
                pass
                
            # Compute Risk
            calc_risk = risk_engine.calculate(dom_res)
            risk_score = calc_risk.get("score", 10)
            risk_level = calc_risk.get("level", "Safe")
            
            recs = ["Audit DNS records periodically for DNS spoofing protection."]
            if not ssl_valid:
                recs.append("Enable SSL/TLS certificates for subdomains to prevent intercept attacks.")
            if registrar == "Unknown":
                recs.append("Verify WHOIS registration details status.")
                
            details = {
                "input_type": "domain",
                "domain": value,
                "registrar": registrar,
                "created_date": created_date,
                "ssl_valid": ssl_valid,
                "ssl_issuer": ssl_issuer,
                "ips": ips,
                "recommendations": recs,
                "domain_data": dom_res,
                "website_data": web_res
            }

        duration = time.time() - start_time
        
        result = {
            "success": True,
            "scanner": "universal_scan",
            "value": value,
            "input_type": input_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "duration": f"{duration:.2f}s",
            "details": details
        }
        
        # Save to SQLite database
        try:
            db.execute(
                """
                INSERT INTO scan_history (scan_type, target, risk_level, risk_score)
                VALUES (?, ?, ?, ?)
                """,
                ("Universal Scan", value, risk_level, float(risk_score))
            )
        except Exception as e:
            logger.error(f"Failed to log universal scan to db: {e}")
            
        return result

universal_scan_module = UniversalScanModule()
