"""
CyberMind AI

IPInfo Service
"""

import requests

from config.api_config import IPINFO_API_KEY
from core.constants import API_TIMEOUT


class IPInfoService:

    BASE_URL = "https://ipinfo.io"

    def available(self) -> bool:
        """
        Check API key.
        """

        return bool(IPINFO_API_KEY)

    def analyze(self, ip: str) -> dict:
        """
        Analyze IP information.
        """
        return self.lookup(ip)

    def lookup(
        self,
        ip: str
    ) -> dict:
        """
        Lookup IP information.
        """

        if not self.available():

            return {

                "success": False,

                "provider": "IPInfo",

                "error": "IPInfo API key not configured."

            }

        try:

            response = requests.get(

                f"{self.BASE_URL}/{ip}/json",

                params={

                    "token": IPINFO_API_KEY

                },

                timeout=API_TIMEOUT

            )

            response.raise_for_status()

            data = response.json()

            latitude = None

            longitude = None

            if "loc" in data:

                try:

                    latitude, longitude = map(

                        float,

                        data["loc"].split(",")

                    )

                except ValueError:

                    pass

            return {

                "success": True,

                "provider": "IPInfo",

                "ip": data.get("ip"),

                "hostname": data.get("hostname"),

                "city": data.get("city"),

                "region": data.get("region"),

                "country": data.get("country"),

                "postal": data.get("postal"),

                "timezone": data.get("timezone"),

                "organization": data.get("org"),

                "latitude": latitude,

                "longitude": longitude,

                "details": data,

                "error": None

            }

        except requests.RequestException as error:

            return {

                "success": False,

                "provider": "IPInfo",

                "details": {},

                "error": str(error)

            }


ipinfo_service = IPInfoService()