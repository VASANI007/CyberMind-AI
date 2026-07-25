"""
CyberMind AI
Macro Detection Service
Detects and extracts macros from Office documents.
Offline — uses oletools library.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.logger import logger


class MacroDetectionService:
    """
    Detects VBA macros in Office documents (.doc, .docx, .xls, .xlsx, .xlsm, .pptm).
    Requires the 'oletools' package.
    """

    OFFICE_EXTENSIONS = {
        ".doc", ".docx", ".docm", ".xls", ".xlsx", ".xlsm",
        ".ppt", ".pptx", ".pptm", ".dot", ".dotm",
    }

    SUSPICIOUS_KEYWORDS = {
        "AutoOpen", "AutoExec", "Auto_Open", "Workbook_Open",
        "Document_Open", "Shell", "WScript", "PowerShell",
        "cmd.exe", "CreateObject", "CallByName", "GetObject",
        "Environ", "URLDownloadToFile", "XMLHTTP", "ADODB",
        "Scripting.FileSystemObject", "WinHttp", "Kill",
    }

    @property
    def name(self) -> str:
        return "macro_detection_service"

    def detect(self, file_path: str) -> dict[str, Any]:
        """
        Detect macros in an Office document.

        Returns
        -------
        dict with keys:
            has_macros        : bool
            macro_count       : int
            macros            : list[dict] — name, code_preview, suspicious_keywords
            suspicious        : bool       — True if suspicious keywords found
            suspicious_items  : list[str]
            risk_contribution : int
        """
        ext = Path(file_path).suffix.lower()

        if ext not in self.OFFICE_EXTENSIONS:
            return {
                "has_macros": False,
                "macro_count": 0,
                "macros": [],
                "suspicious": False,
                "suspicious_items": [],
                "risk_contribution": 0,
                "note": "Not an Office file",
            }

        try:
            from oletools.olevba import VBA_Parser
        except ImportError:
            logger.warning("oletools not installed — macro detection skipped")
            return {
                "has_macros": False,
                "macro_count": 0,
                "macros": [],
                "suspicious": False,
                "suspicious_items": [],
                "risk_contribution": 0,
                "error": "oletools not installed",
            }

        macros_found = []
        suspicious_items = []

        try:
            vba_parser = VBA_Parser(file_path)

            if not vba_parser.detect_vba_macros():
                vba_parser.close()
                return {
                    "has_macros": False,
                    "macro_count": 0,
                    "macros": [],
                    "suspicious": False,
                    "suspicious_items": [],
                    "risk_contribution": 0,
                }

            for (filename, stream_path, vba_filename, vba_code) in vba_parser.extract_macros():
                code_str = vba_code if isinstance(vba_code, str) else vba_code.decode("utf-8", errors="replace")

                # Check for suspicious keywords
                found_keywords = []
                for kw in self.SUSPICIOUS_KEYWORDS:
                    if kw.lower() in code_str.lower():
                        found_keywords.append(kw)
                        if kw not in suspicious_items:
                            suspicious_items.append(kw)

                macros_found.append({
                    "name": vba_filename or stream_path or "Unknown",
                    "code_preview": code_str[:200] + ("..." if len(code_str) > 200 else ""),
                    "code_length": len(code_str),
                    "suspicious_keywords": found_keywords,
                })

            vba_parser.close()

        except Exception as exc:
            logger.warning("Macro detection error: %s", exc)
            return {
                "has_macros": False,
                "macro_count": 0,
                "macros": [],
                "suspicious": False,
                "suspicious_items": [],
                "risk_contribution": 0,
                "error": str(exc),
            }

        is_suspicious = len(suspicious_items) > 0
        risk = 0
        if macros_found:
            risk = 15
        if is_suspicious:
            risk = 30 + min(len(suspicious_items) * 5, 20)

        return {
            "has_macros": len(macros_found) > 0,
            "macro_count": len(macros_found),
            "macros": macros_found[:10],
            "suspicious": is_suspicious,
            "suspicious_items": suspicious_items,
            "risk_contribution": min(risk, 50),
        }

    def analyze(self, file_path: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.detect(file_path)

    def health_check(self) -> dict[str, Any]:
        try:
            from oletools.olevba import VBA_Parser
            return {"service": "Macro Detection Service", "status": "Healthy"}
        except ImportError:
            return {"service": "Macro Detection Service", "status": "Degraded", "note": "oletools not installed"}


macro_detection_service = MacroDetectionService()
