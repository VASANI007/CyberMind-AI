"""
CyberMind AI

Scanner Engine

Enterprise Production Version
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.logger import logger

from modules.url_scanner import (
    url_scanner
)

from modules.website_scanner import (
    website_scanner
)

from modules.domain_scanner import (
    domain_scanner
)

from modules.email_scanner import (
    email_scanner
)

from modules.ip_scanner import (
    ip_scanner
)

from modules.file_scanner import (
    file_scanner
)

from modules.qr_scanner import (
    qr_scanner
)


class ScannerEngine:
    """
    CyberMind AI Master Scanner.

    Responsibilities

    • Input Detection

    • Scanner Selection

    • Scanner Routing

    • Batch Scanning

    • Statistics

    • History

    • Unified Response
    """

    URL_PATTERN = re.compile(

        r"^https?://",

        re.IGNORECASE

    )

    EMAIL_PATTERN = re.compile(

        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    )

    IPV4_PATTERN = re.compile(

        r"^((25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}"
        r"(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})$"

    )

    DOMAIN_PATTERN = re.compile(

        r"^(?!:\/\/)([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"

    )

    FILE_EXTENSIONS = {

        ".pdf",

        ".doc",

        ".docx",

        ".xls",

        ".xlsx",

        ".ppt",

        ".pptx",

        ".txt",

        ".csv",

        ".zip",

        ".rar",

        ".7z",

        ".exe",

        ".apk",

        ".png",

        ".jpg",

        ".jpeg",

        ".gif",

        ".bmp",

        ".webp"

    }

    def __init__(
        self
    ) -> None:

        logger.info(

            "Scanner Engine initialized."

        )

        self.scanners = {

            "url":

                url_scanner,

            "website":

                website_scanner,

            "domain":

                domain_scanner,

            "email":

                email_scanner,

            "ip":

                ip_scanner,

            "file":

                file_scanner,

            "qr":

                qr_scanner

        }

        self.history = []

        self.statistics = {

            "total_scans": 0,

            "url": 0,

            "website": 0,

            "domain": 0,

            "email": 0,

            "ip": 0,

            "file": 0,

            "qr": 0

        }

    def available_scanners(
        self
    ) -> list[str]:
        """
        Return available scanners.
        """

        return list(

            self.scanners.keys()

        )

    def scanner(
        self,
        name: str
    ):
        """
        Return scanner object.
        """

        return self.scanners.get(

            name.lower()

        )

    def supported_file_extensions(
        self
    ) -> list[str]:
        """
        Supported file extensions.
        """

        return sorted(

            self.FILE_EXTENSIONS

        )
        
        
    def is_url(
        self,
        value: str
    ) -> bool:
        """
        Detect URL.
        """

        return bool(

            self.URL_PATTERN.match(

                value.strip()

            )

        )

    def is_email(
        self,
        value: str
    ) -> bool:
        """
        Detect email.
        """

        return bool(

            self.EMAIL_PATTERN.fullmatch(

                value.strip()

            )

        )

    def is_ipv4(
        self,
        value: str
    ) -> bool:
        """
        Detect IPv4.
        """

        return bool(

            self.IPV4_PATTERN.fullmatch(

                value.strip()

            )

        )

    def is_domain(
        self,
        value: str
    ) -> bool:
        """
        Detect domain.
        """

        value = value.strip().lower()

        if self.is_url(value):

            return False

        if self.is_email(value):

            return False

        if self.is_ipv4(value):

            return False

        return bool(

            self.DOMAIN_PATTERN.fullmatch(

                value

            )

        )

    def is_file(
        self,
        value: str
    ) -> bool:
        """
        Detect local file.
        """

        path = Path(

            value

        )

        return (

            path.exists()

            and

            path.is_file()

        )

    def is_supported_file(
        self,
        value: str
    ) -> bool:
        """
        Supported file type.
        """

        extension = Path(

            value

        ).suffix.lower()

        return (

            extension

            in

            self.FILE_EXTENSIONS

        )

    def detect(
        self,
        value: str
    ) -> str:
        """
        Auto detect scanner type.
        """

        value = value.strip()

        if self.is_email(

            value

        ):

            return "email"

        if self.is_ipv4(

            value

        ):

            return "ip"

        if self.is_url(

            value

        ):

            return "website"

        if self.is_domain(

            value

        ):

            return "domain"

        if self.is_file(

            value

        ):

            extension = (

                Path(

                    value

                )

                .suffix

                .lower()

            )

            if extension in {

                ".png",

                ".jpg",

                ".jpeg",

                ".bmp",

                ".gif",

                ".webp"

            }:

                return "qr"

            return "file"

        return "unknown"
    
    
    
    def scan(
        self,
        value: str,
        scanner_type: str | None = None
    ) -> dict[str, Any]:
        """
        Scan input using automatic
        or manual scanner selection.
        """

        value = value.strip()

        if scanner_type is None:

            scanner_type = self.detect(

                value

            )

        scanner = self.scanner(

            scanner_type

        )

        if scanner is None:

            logger.warning(

                "Unknown scanner type : %s",

                scanner_type

            )

            return {

                "success": False,

                "scanner": scanner_type,

                "message": "Unsupported scanner."

            }

        logger.info(

            "Using %s scanner.",

            scanner_type

        )

        result = scanner.analyze(

            value

        )

        self.statistics[

            "total_scans"

        ] += 1

        if scanner_type in self.statistics:

            self.statistics[

                scanner_type

            ] += 1

        self.history.append(

            {

                "scanner":

                    scanner_type,

                "input":

                    value,

                "success":

                    result.get(

                        "success",

                        False

                    )

            }

        )

        return {

            "success": True,

            "scanner": scanner_type,

            "result": result

        }

    def batch_scan(
        self,
        values: list[str]
    ) -> list[dict[str, Any]]:
        """
        Scan multiple inputs.
        """

        results = []

        for value in values:

            results.append(

                self.scan(

                    value

                )

            )

        return results

    def statistics_report(
        self
    ) -> dict[str, int]:
        """
        Return scan statistics.
        """

        return self.statistics.copy()

    def scan_history(
        self
    ) -> list[dict[str, Any]]:
        """
        Return scan history.
        """

        return self.history.copy()

    def clear_history(
        self
    ) -> None:
        """
        Clear scan history.
        """

        self.history.clear()

        logger.info(

            "Scanner history cleared."

        )
        

    def registered_scanners(
        self
    ) -> dict[str, str]:
        """
        Return registered scanners.
        """

        return {

            name:

                scanner.__class__.__name__

            for name,

            scanner

            in self.scanners.items()

        }

    def total_scans(
        self
    ) -> int:
        """
        Total scans.
        """

        return self.statistics.get(

            "total_scans",

            0

        )

    def summary(
        self
    ) -> dict[str, Any]:
        """
        Scanner summary.
        """

        return {

            "registered_scanners":

                len(

                    self.scanners

                ),

            "available":

                self.available_scanners(),

            "total_scans":

                self.total_scans(),

            "history":

                len(

                    self.history

                )

        }

    def reset_statistics(
        self
    ) -> None:
        """
        Reset statistics.
        """

        for key in self.statistics:

            self.statistics[

                key

            ] = 0

        logger.info(

            "Scanner statistics reset."

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Engine health.
        """

        scanners = {}

        for name, scanner in self.scanners.items():

            try:

                if hasattr(

                    scanner,

                    "health_check"

                ):

                    scanners[

                        name

                    ] = scanner.health_check()

                else:

                    scanners[

                        name

                    ] = {

                        "status":

                            "Unknown"

                    }

            except Exception as error:

                logger.exception(

                    error

                )

                scanners[

                    name

                ] = {

                    "status":

                        "Failed"

                }

        return {

            "engine":

                "Scanner Engine",

            "status":

                "Healthy",

            "registered":

                len(

                    self.scanners

                ),

            "scanners":

                scanners

        }

    def version(
        self
    ) -> str:
        """
        Engine version.
        """

        return "2.0.0"

    def __repr__(
        self
    ) -> str:

        return (

            "ScannerEngine("

            "Enterprise Version)"

        )


scanner_engine = ScannerEngine()