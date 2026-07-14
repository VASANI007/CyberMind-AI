"""
CyberMind AI

TLD Service
"""

from pathlib import Path

from config.settings import DATASET_PATH


class TLDService:

    def __init__(self):

        self.tlds = self.load_tlds()

    def load_tlds(self) -> set:
        """
        Load all valid TLDs.
        """

        tld_file = (
            DATASET_PATH
            / "datasets"
            / "domain"
            / "raw"
            / "tlds-alpha-by-domain.txt"
        )

        if not tld_file.exists():

            return set()

        tlds = set()

        with open(
            tld_file,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if (

                    line

                    and

                    not line.startswith("#")

                ):

                    tlds.add(
                        line.lower()
                    )

        return tlds

    def get_tld(
        self,
        domain: str
    ) -> str:
        """
        Return TLD.
        """

        if "." not in domain:

            return ""

        return domain.split(".")[-1].lower()

    def is_valid_tld(
        self,
        domain: str
    ) -> bool:
        """
        Check valid TLD.
        """

        return (

            self.get_tld(domain)

            in

            self.tlds

        )

    def tld_exists(
        self,
        tld: str
    ) -> bool:
        """
        Check TLD exists.
        """

        return (

            tld.lower()

            in

            self.tlds

        )

    def total_tlds(
        self
    ) -> int:
        """
        Total loaded TLDs.
        """

        return len(
            self.tlds
        )

    def analyze(
        self,
        domain: str
    ) -> dict:
        """
        Analyze domain TLD.
        """

        tld = self.get_tld(
            domain
        )

        return {

            "domain": domain,

            "tld": tld,

            "valid": self.is_valid_tld(
                domain
            )

        }


tld_service = TLDService()