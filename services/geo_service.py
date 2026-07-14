"""
CyberMind AI

Geo Service
"""

from pathlib import Path

import geoip2.database

from config.settings import DATASET_PATH
from core.logger import logger


class GeoService:

    def __init__(self):

        self.database = (
            DATASET_PATH
            / "datasets"
            / "ip"
            / "raw"
            / "GeoLite2-City.mmdb"
        )

        self.reader = None

        if self.database.exists():

            self.reader = geoip2.database.Reader(
                str(self.database)
            )
        
        if self.reader is None:
            logger.error(f"GeoLite2-City.mmdb is missing or reader is None at path: {self.database}")

    def analyze(self, ip: str) -> dict:
        """
        Analyze IP geo location.
        """
        return self.lookup(ip)

    def lookup(
        self,
        ip: str
    ) -> dict:
        """
        Lookup IP location.
        """

        if self.reader is None:

            return {}

        try:

            response = self.reader.city(ip)

            return {

                "ip": ip,

                "country": response.country.name,

                "country_code": response.country.iso_code,

                "city": response.city.name,

                "state": response.subdivisions.most_specific.name,

                "postal_code": response.postal.code,

                "latitude": response.location.latitude,

                "longitude": response.location.longitude,

                "timezone": response.location.time_zone,

                "continent": response.continent.name

            }

        except Exception:

            return {}

    def country(
        self,
        ip: str
    ) -> str:

        return self.lookup(ip).get(
            "country"
        )

    def city(
        self,
        ip: str
    ) -> str:

        return self.lookup(ip).get(
            "city"
        )

    def coordinates(
        self,
        ip: str
    ) -> tuple:

        result = self.lookup(ip)

        return (

            result.get("latitude"),

            result.get("longitude")

        )


geo_service = GeoService()