"""
CyberMind AI

AbuseIPDB Service
"""

import requests

from config.api_config import (
    ABUSEIPDB_API_KEY
)

from core.constants import API_TIMEOUT


class AbuseIPDBService:

    BASE_URL = "https://api.abuseipdb.com/api/v2/check"

    def available(self) -> bool:
        """
        Check API key.
        """

        return bool(ABUSEIPDB_API_KEY)

    def lookup(self, ip: str) -> dict:
        """
        Lookup IP reputation.
        """
        return self.check(ip)

    def check(
        self,
        ip: str,
        max_age: int = 90
    ) -> dict:
        """
        Check IP reputation.
        """

        if not self.available():

            return {

                "success": False,

                "error": "AbuseIPDB API key not configured."

            }

        try:

            response = requests.get(

                self.BASE_URL,

                headers={

                    "Key": ABUSEIPDB_API_KEY,

                    "Accept": "application/json"

                },

                params={

                    "ipAddress": ip,

                    "maxAgeInDays": max_age

                },

                timeout=API_TIMEOUT

            )

            response.raise_for_status()

            data = response.json().get(

                "data",

                {}

            )

            return {

                "success": True,

                "provider": "AbuseIPDB",

                "malicious": data.get(

                    "abuseConfidenceScore",

                    0

                ) >= 50,

                "risk_score": data.get(

                    "abuseConfidenceScore",

                    0

                ),

                "country": data.get(

                    "countryCode"

                ),

                "isp": data.get(

                    "isp"

                ),

                "domain": data.get(

                    "domain"

                ),

                "usage_type": data.get(

                    "usageType"

                ),

                "total_reports": data.get(

                    "totalReports"

                ),

                "last_reported_at": data.get(

                    "lastReportedAt"

                ),

                "details": data,

                "error": None

            }

        except requests.RequestException as error:

            return {

                "success": False,

                "provider": "AbuseIPDB",

                "malicious": False,

                "risk_score": 0,

                "details": {},

                "error": str(error)

            }


abuseipdb_service = AbuseIPDBService()