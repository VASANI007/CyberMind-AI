"""
CyberMind AI

File Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.file_scanner import FileScanner


class FileModule(FileScanner):
    """
    File Module wrapping FileScanner.
    """

    def __repr__(self) -> str:
        return "FileModule(Enterprise Version)"


file_module = FileModule()
