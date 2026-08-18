"""
CyberMind AI

Geo Service
"""

try:
    import geoip2.database
    HAS_GEOIP2 = True
except ImportError:
    HAS_GEOIP2 = False

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

        if HAS_GEOIP2 and self.database.exists():
            try:
                self.reader = geoip2.database.Reader(
                    str(self.database)
                )
            except Exception as e:
                logger.warning(f"Could not open GeoLite2 database: {e}")
                self.reader = None
        elif not HAS_GEOIP2:
            logger.info("geoip2 module not installed; running GeoService in lightweight fallback mode.")
        elif not self.database.exists():
            logger.info(f"GeoLite2-City.mmdb dataset not found at path: {self.database}")


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