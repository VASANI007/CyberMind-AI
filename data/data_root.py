"""
CyberMind AI
Data Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from pathlib import Path
from typing import Any

from core.logger import logger
from config.paths import DATA_DIR


class DataRoot:
    """
    Enterprise Data Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.base_path = Path(DATA_DIR)

        self.folders = {

            "blacklist":
                self.base_path / "blacklist",

            "datasets":
                self.base_path / "datasets",

            "disposable_email":
                self.base_path / "disposable_email",

            "domain":
                self.base_path / "domain",

            "email":
                self.base_path / "email",

            "files":
                self.base_path / "files",

            "ip":
                self.base_path / "ip",

            "phishing":
                self.base_path / "phishing",

            "samples":
                self.base_path / "samples",

            "security":
                self.base_path / "security"

        }

        self.dataset_registry = {

            "url": [

                "online-valid.csv",

                "openphish_feed.txt",

                "PhishURL_Phishing_URL_Dataset.csv",

                "top-1m.csv"

            ],

            "website": [

                "http_status_codes.csv",

                "security_headers.json",

                "tls_versions.csv",

                "tls_cipher_suites.csv"

            ],

            "domain": [

                "accredited-registrars.csv",

                "public_suffix_list.dat",

                "tlds-alpha-by-domain.txt"

            ],

            "email": [

                "domains.json",

                "disposable_email_blocklist.conf"

            ],

            "file": [

                "file_signatures.csv",

                "triddefs.trd"

            ],

            "ip": [

                "GeoLite2-ASN-CSV.zip",

                "GeoLite2-Country-CSV.zip",

                "GeoLite2-City-CSV.zip"

            ],

            "qr": [

                "malicious_qr_payloads.csv",

                "safe_qr_payloads.csv"

            ],

            "shared": [

                "countries.csv",

                "dns_record_types.csv",

                "file_extensions.csv",

                "http_methods.csv",

                "mime_types.csv",

                "ports.csv",

                "risk_levels.csv"

            ]

        }

        logger.info(
            "Data Root Initialized."
        )

    def initialize(self) -> None:
        """
        Initialize data layer.
        """

        logger.info(
            "Initializing Data Manager..."
        )

        self.verify_folders()

        self.verify_datasets()

        logger.info(
            "Data Manager Ready."
        )

    def verify_folders(self) -> bool:
        """
        Verify required folders.
        """

        healthy = True

        for name, folder in self.folders.items():

            if folder.exists():

                logger.info(
                    "%s ✓",
                    name
                )

            else:

                logger.warning(
                    "%s ✗ Missing",
                    name
                )

                healthy = False

        return healthy

    def verify_datasets(self) -> bool:
        """
        Verify dataset structure.
        """

        healthy = True

        datasets_path = (

            self.base_path /

            "datasets"

        )

        for category in self.dataset_registry:

            category_path = (

                datasets_path /

                category /

                "raw"

            )

            if category_path.exists():

                logger.info(
                    "%s Dataset ✓",
                    category.upper()
                )

            else:

                logger.warning(
                    "%s Dataset Missing",
                    category.upper()
                )

                healthy = False

        return healthy
    
    def total_folders(self) -> int:
        """
        Return total registered folders.
        """

        return len(self.folders)

    def total_categories(self) -> int:
        """
        Return total dataset categories.
        """

        return len(self.dataset_registry)

    def total_dataset_files(self) -> int:
        """
        Return total registered dataset files.
        """

        return sum(
            len(files)
            for files in self.dataset_registry.values()
        )

    def list_folders(self) -> list[str]:
        """
        Return all folders.
        """

        return sorted(
            self.folders.keys()
        )

    def list_categories(self) -> list[str]:
        """
        Return dataset categories.
        """

        return sorted(
            self.dataset_registry.keys()
        )

    def list_dataset_files(
        self,
        category: str
    ) -> list[str]:
        """
        Return files for category.
        """

        return self.dataset_registry.get(
            category.lower(),
            []
        )

    def get_dataset_path(
        self,
        category: str,
        filename: str
    ) -> Path:
        """
        Return dataset path.
        """

        return (
            self.base_path
            / "datasets"
            / category
            / "raw"
            / filename
        )

    def dataset_exists(
        self,
        category: str,
        filename: str
    ) -> bool:
        """
        Check dataset exists.
        """

        return self.get_dataset_path(
            category,
            filename
        ).exists()

    def find_dataset(
        self,
        filename: str
    ) -> Path | None:
        """
        Search dataset.
        """

        for category in self.dataset_registry:

            path = self.get_dataset_path(
                category,
                filename
            )

            if path.exists():

                return path

        return None

    def count_files(
        self,
        extension: str
    ) -> int:
        """
        Count files by extension.
        """

        return len(

            list(

                self.base_path.rglob(
                    f"*{extension}"
                )

            )

        )

    def dataset_statistics(
        self
    ) -> dict[str, Any]:
        """
        Dataset statistics.
        """

        return {

            "folders":
                self.total_folders(),

            "categories":
                self.total_categories(),

            "registered_files":
                self.total_dataset_files(),

            "csv":
                self.count_files(".csv"),

            "txt":
                self.count_files(".txt"),

            "json":
                self.count_files(".json"),

            "zip":
                self.count_files(".zip"),

            "md":
                self.count_files(".md"),

            "conf":
                self.count_files(".conf"),

            "dat":
                self.count_files(".dat"),

            "trd":
                self.count_files(".trd"),

            "arff":
                self.count_files(".arff")

        }

    def list_all_files(
        self
    ) -> list[Path]:
        """
        Return every file.
        """

        return sorted(

            self.base_path.rglob("*")

        )
        
    def create_missing_directories(self) -> None:
        """
        Create missing directories.
        """

        for folder in self.folders.values():

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

        logger.info(
            "All required directories verified."
        )

    def verify_readme(self) -> bool:
        """
        Verify README file.
        """

        readme = self.base_path / "README.md"

        exists = readme.exists()

        if exists:

            logger.info(
                "README.md found."
            )

        else:

            logger.warning(
                "README.md missing."
            )

        return exists

    def health_check(self) -> dict[str, Any]:
        """
        Data layer health check.
        """

        folders_ok = self.verify_folders()

        datasets_ok = self.verify_datasets()

        readme_ok = self.verify_readme()

        stats = self.dataset_statistics()

        return {

            "service": "Data",

            "status": (

                "Healthy"

                if (

                    folders_ok

                    and

                    datasets_ok

                )

                else

                "Unhealthy"

            ),

            "folders": stats["folders"],

            "categories": stats["categories"],

            "registered_files": stats["registered_files"],

            "csv": stats["csv"],

            "txt": stats["txt"],

            "json": stats["json"],

            "zip": stats["zip"],

            "readme": readme_ok

        }

    def status(self) -> dict[str, Any]:
        """
        Current status.
        """

        return {

            "version": self.VERSION,

            "base_directory": str(
                self.base_path
            ),

            "health": self.health_check(),

            "statistics": self.dataset_statistics()

        }

    def reload(self) -> None:
        """
        Reload data manager.
        """

        logger.info(
            "Reloading data manager..."
        )

        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown data manager.
        """

        logger.info(
            "Data manager shutdown."
        )

    def __len__(self) -> int:
        """
        Total registered dataset files.
        """

        return self.total_dataset_files()

    def __repr__(self) -> str:
        """
        String representation.
        """

        return (

            f"DataRoot("
            f"folders={self.total_folders()}, "
            f"categories={self.total_categories()}, "
            f"datasets={self.total_dataset_files()}, "
            f"version='{self.VERSION}')"

        )


data_root = DataRoot()