"""
CyberMind AI
Hex Signature Service
Identifies file types from magic bytes (file signatures).
Offline — pure Python magic-byte lookup, no external dependency.
"""

from __future__ import annotations

from typing import Any

from core.logger import logger


# Magic byte signatures: (hex_prefix, file_type, description, category)
MAGIC_SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", "PNG", "PNG Image", "Image"),
    (b"\xff\xd8\xff", "JPEG", "JPEG Image", "Image"),
    (b"GIF87a", "GIF", "GIF Image (87a)", "Image"),
    (b"GIF89a", "GIF", "GIF Image (89a)", "Image"),
    (b"BM", "BMP", "Bitmap Image", "Image"),
    (b"II\x2a\x00", "TIFF", "TIFF Image (LE)", "Image"),
    (b"MM\x00\x2a", "TIFF", "TIFF Image (BE)", "Image"),
    (b"\x00\x00\x01\x00", "ICO", "Windows Icon", "Image"),
    (b"RIFF", "RIFF", "RIFF Container (AVI/WAV)", "Multimedia"),
    (b"\x1a\x45\xdf\xa3", "MKV/WebM", "Matroska/WebM Video", "Multimedia"),
    (b"\x00\x00\x00\x18ftypmp4", "MP4", "MPEG-4 Video", "Multimedia"),
    (b"\x00\x00\x00\x1cftyp", "MP4", "MPEG-4 Container", "Multimedia"),
    (b"ID3", "MP3", "MP3 Audio (ID3)", "Audio"),
    (b"\xff\xfb", "MP3", "MP3 Audio", "Audio"),
    (b"\xff\xf3", "MP3", "MP3 Audio (MPEG2)", "Audio"),
    (b"OggS", "OGG", "Ogg Vorbis Audio", "Audio"),
    (b"fLaC", "FLAC", "FLAC Audio", "Audio"),
    (b"PK\x03\x04", "ZIP", "ZIP Archive", "Archive"),
    (b"PK\x05\x06", "ZIP", "ZIP Archive (empty)", "Archive"),
    (b"\x1f\x8b", "GZIP", "GZIP Compressed", "Archive"),
    (b"Rar!\x1a\x07", "RAR", "RAR Archive", "Archive"),
    (b"\x37\x7a\xbc\xaf\x27\x1c", "7Z", "7-Zip Archive", "Archive"),
    (b"\xfd\x37\x7a\x58\x5a\x00", "XZ", "XZ Compressed", "Archive"),
    (b"BZh", "BZ2", "BZip2 Compressed", "Archive"),
    (b"MZ", "EXE/DLL", "Windows PE Executable", "Executable"),
    (b"\x7fELF", "ELF", "Linux ELF Executable", "Executable"),
    (b"\xfe\xed\xfa", "Mach-O", "macOS Mach-O Binary", "Executable"),
    (b"\xcf\xfa\xed\xfe", "Mach-O", "macOS Mach-O Binary (64)", "Executable"),
    (b"\xca\xfe\xba\xbe", "Java/Mach-O", "Java Class / Universal Binary", "Executable"),
    (b"%PDF", "PDF", "PDF Document", "Document"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "OLE", "MS Office Document (OLE)", "Document"),
    (b"{\\rtf", "RTF", "Rich Text Format", "Document"),
    (b"SQLite format 3", "SQLite", "SQLite Database", "Database"),
    (b"\x00\x00\x00\x0c\x6a\x50\x20\x20", "JPEG2000", "JPEG 2000 Image", "Image"),
    (b"\x50\x4b\x03\x04\x14\x00\x06\x00", "DOCX/XLSX", "Office Open XML", "Document"),
]


class HexSignatureService:
    """
    Identifies file type from magic bytes (first N bytes of file).
    """

    @property
    def name(self) -> str:
        return "hex_signature_service"

    def identify(self, file_bytes: bytes) -> dict[str, Any]:
        """
        Identify file type from magic bytes.

        Parameters
        ----------
        file_bytes : first 32+ bytes of the file

        Returns
        -------
        dict with keys:
            detected     : bool
            file_type    : str
            description  : str
            category     : str
            hex_preview  : str  — first 16 bytes as hex string
        """
        if not file_bytes:
            return {
                "detected": False,
                "file_type": "Unknown",
                "description": "Empty file",
                "category": "Unknown",
                "hex_preview": "",
            }

        hex_preview = " ".join(f"{b:02X}" for b in file_bytes[:16])

        for sig_bytes, file_type, description, category in MAGIC_SIGNATURES:
            if file_bytes[:len(sig_bytes)] == sig_bytes:
                return {
                    "detected": True,
                    "file_type": file_type,
                    "description": description,
                    "category": category,
                    "hex_preview": hex_preview,
                }

        return {
            "detected": False,
            "file_type": "Unknown",
            "description": "Unrecognized file signature",
            "category": "Unknown",
            "hex_preview": hex_preview,
        }

    def analyze(self, file_bytes: bytes) -> dict[str, Any]:
        """Plugin interface."""
        return self.identify(file_bytes)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Hex Signature Service",
            "status": "Healthy",
            "signatures": len(MAGIC_SIGNATURES),
        }


hex_signature_service = HexSignatureService()
