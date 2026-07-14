"""
CyberMind AI

Blacklist Service
"""

from pathlib import Path
from urllib.parse import urlparse

from config.settings import DATASET_PATH


class BlacklistService:

    def __init__(self):

        self.blacklist = set()

        self.load()

    def load(self):
        """
        Load blacklist datasets.
        """

        files = [

            DATASET_PATH
            / "datasets"
            / "url"
            / "raw"
            / "openphish_feed.txt",

            DATASET_PATH
            / "datasets"
            / "url"
            / "raw"
            / "phishtank_urls.csv"

        ]

        for file in files:

            if not file.exists():

                continue

            with open(
                file,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                for line in f:

                    line = line.strip()

                    if not line:

                        continue

                    if "," in line:

                        line = line.split(",")[0]

                    self.blacklist.add(
                        line.lower()
                    )

    def normalize(
        self,
        url: str
    ) -> str:
        """
        Normalize URL.
        """

        parsed = urlparse(url)

        return parsed.geturl().lower()

    def domain(
        self,
        url: str
    ) -> str:
        """
        Extract domain.
        """

        parsed = urlparse(url)

        return (

            parsed.hostname or ""

        ).lower()

    def is_blacklisted(
        self,
        url: str
    ) -> bool:
        """
        Check blacklist.
        """

        url = self.normalize(url)

        domain = self.domain(url)

        if url in self.blacklist:

            return True

        if domain in self.blacklist:

            return True

        return False

    def analyze(
        self,
        url: str
    ) -> dict:
        """
        Analyze blacklist.
        """

        return {

            "url": url,

            "blacklisted": self.is_blacklisted(
                url
            )

        }

    def lookup(self, target: str) -> dict:
        """
        Lookup target in blacklist.
        """
        return self.analyze(target)


    def total_entries(
        self
    ) -> int:
        """
        Total blacklist entries.
        """

        return len(
            self.blacklist
        )


blacklist_service = BlacklistService()