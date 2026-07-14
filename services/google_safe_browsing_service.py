"""
CyberMind AI

Google Safe Browsing Service
"""

import requests

from config.api_config import (
    GOOGLE_SAFE_BROWSING_API_KEY,
    HEADERS
)

from core.constants import API_TIMEOUT


class GoogleSafeBrowsingService:

    BASE_URL = (
        "https://safebrowsing.googleapis.com/v4/"
        "threatMatches:find"
    )

    def available(self) -> bool:
        """
        Check API key.
        """

        return bool(
            GOOGLE_SAFE_BROWSING_API_KEY
        )

    def scan(
        self,
        url: str
    ) -> dict:
        """
        Scan URL using Google Safe Browsing.
        """

        if not self.available():

            return {

                "success": False,

                "error": "Google Safe Browsing API key not configured."

            }

        payload = {

            "client": {

                "clientId": "CyberMind AI",

                "clientVersion": "1.0"

            },

            "threatInfo": {

                "threatTypes": [

                    "MALWARE",

                    "SOCIAL_ENGINEERING",

                    "UNWANTED_SOFTWARE",

                    "POTENTIALLY_HARMFUL_APPLICATION"

                ],

                "platformTypes": [

                    "ANY_PLATFORM"

                ],

                "threatEntryTypes": [

                    "URL"

                ],

                "threatEntries": [

                    {

                        "url": url

                    }

                ]

            }

        }

        try:

            response = requests.post(

                self.BASE_URL,

                params={

                    "key": GOOGLE_SAFE_BROWSING_API_KEY

                },

                json=payload,

                headers=HEADERS,

                timeout=API_TIMEOUT

            )

            response.raise_for_status()

            result = response.json()

            matches = result.get(

                "matches",

                []

            )

            return {

                "success": True,

                "safe": len(matches) == 0,

                "malicious": len(matches) > 0,

                "matches": matches,

                "threat_count": len(matches)

            }

        except requests.RequestException as error:

            return {

                "success": False,

                "error": str(error)

            }


google_safe_browsing_service = GoogleSafeBrowsingService()