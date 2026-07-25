"""
CyberMind AI
Recommendation Service
Provides templated security recommendations as offline fallbacks when AI APIs are unavailable.
Offline — static rules engine.
"""

from __future__ import annotations
from typing import Any


class RecommendationService:
    """
    Offline fallback engine for security recommendations and advice.
    """

    RECOMMENDATIONS = {
        "URL Scanner": [
            "Do not enter personal credentials or passwords on unverified domain names.",
            "Verify HTTPS certificate details and check for subtle domain spelling variations.",
            "Utilize a web reputation browser extension to automatically block malicious redirects.",
            "Inspect URL query parameters for embedded executable scripts or base64 blobs."
        ],
        "Website Scanner": [
            "Ensure all Web Server security headers (CSP, HSTS, X-Frame-Options) are strictly enforced.",
            "Keep underlying CMS frameworks (WordPress, Drupal, etc.) and plugins fully updated.",
            "Disable directory listing and obscure backend administration login paths.",
            "Implement Web Application Firewall (WAF) rules to filter SQLi and XSS payloads."
        ],
        "Domain Scanner": [
            "Monitor Domain Registrations for typosquatting and homograph variations of your brand.",
            "Enable DNSSEC to prevent DNS spoofing and cache poisoning attacks.",
            "Review WHOIS contact information and ensure privacy protection is enabled.",
            "Audit Certificate Transparency (CT) logs regularly for unauthorized SSL cert issuance."
        ],
        "IP Scanner": [
            "Block inbound connections from known TOR Exit Nodes and unverified VPN proxies if appropriate.",
            "Restrict access to administrative ports (22 SSH, 3389 RDP) using IP whitelisting.",
            "Inspect network flow telemetry for anomalous traffic spikes or beaconing activity.",
            "Ensure geo-blocking policies are active for high-risk foreign IP ranges."
        ],
        "Email Scanner": [
            "Configure strict SPF, DKIM, and DMARC (p=reject) DNS authentication records.",
            "Do not click links or download attachments from disposable or unverified email domains.",
            "Enable Multi-Factor Authentication (MFA) across all organizational email accounts.",
            "Educate users to spot spearphishing tactics, fake urgency, and spoofed display names."
        ],
        "File Scanner": [
            "Never execute suspicious files downloaded from unknown web sources or email links.",
            "Disable VBA macro execution by default in Microsoft Office applications.",
            "Run unfamiliar binaries inside an isolated sandbox environment before local execution.",
            "Verify file digital signatures and SHA256 hashes against published publisher checksums."
        ],
        "QR Code Scanner": [
            "Inspect decoded QR target URLs carefully before opening them in a browser.",
            "Never approve payment requests or enter PIN numbers triggered directly by a QR scan.",
            "Use a secure QR reader that displays the full expanded destination URL first.",
            "Beware of physical QR stickers pasted over legitimate promotional posters or payment terminals."
        ]
    }

    @property
    def name(self) -> str:
        return "recommendation_service"

    def get_recommendations(self, scanner_key: str, risk_score: float = 50.0) -> list[str]:
        """
        Get tailored recommendations for a scanner category.
        """
        recs = self.RECOMMENDATIONS.get(scanner_key, [
            "Maintain updated endpoint antivirus and firewall configurations.",
            "Regularly back up critical data to offline or immutable cloud storage.",
            "Enforce strong, unique passwords and Multi-Factor Authentication (MFA)."
        ])

        if risk_score >= 70:
            recs.insert(0, "🚨 CRITICAL: Immediately isolate the affected endpoint or network asset.")

        return recs

    def analyze(self, scanner_key: str, risk_score: float = 50.0) -> list[str]:
        """Plugin interface."""
        return self.get_recommendations(scanner_key, risk_score)

    def health_check(self) -> dict[str, Any]:
        return {"service": "Recommendation Service", "status": "Healthy"}


recommendation_service = RecommendationService()
