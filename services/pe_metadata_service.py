"""
CyberMind AI
PE Metadata Service
Extracts metadata from Windows PE executables.
Offline — uses pefile library.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

from core.logger import logger


class PEMetadataService:
    """
    Extracts metadata from Windows PE files (.exe, .dll, .sys).
    Requires the 'pefile' package.
    """

    @property
    def name(self) -> str:
        return "pe_metadata_service"

    def extract(self, file_path: str) -> dict[str, Any]:
        """
        Extract PE metadata from *file_path*.

        Returns
        -------
        dict with keys:
            is_pe           : bool
            machine         : str
            compile_time    : str
            sections        : list[dict]
            imports         : list[dict]
            entry_point     : str
            image_base      : str
            subsystem       : str
            is_dll          : bool
            is_packed       : bool  — heuristic: high-entropy + few imports
            suspicious_imports : list[str]
        """
        try:
            import pefile
        except ImportError:
            logger.warning("pefile not installed — PE analysis skipped")
            return {"is_pe": False, "error": "pefile not installed"}

        try:
            pe = pefile.PE(file_path, fast_load=False)
        except pefile.PEFormatError:
            return {"is_pe": False, "error": "Not a valid PE file"}
        except Exception as exc:
            logger.warning("PE parse error: %s", exc)
            return {"is_pe": False, "error": str(exc)}

        # Machine type
        machine_map = {
            0x14C: "x86 (32-bit)",
            0x8664: "x64 (64-bit)",
            0x1C0: "ARM",
            0xAA64: "ARM64",
        }
        machine = machine_map.get(
            pe.FILE_HEADER.Machine, f"0x{pe.FILE_HEADER.Machine:04X}"
        )

        # Compile timestamp
        try:
            ts = pe.FILE_HEADER.TimeDateStamp
            compile_time = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception:
            compile_time = "Unknown"

        # Sections
        sections = []
        for section in pe.sections:
            try:
                name = section.Name.decode("utf-8", errors="replace").strip("\x00")
            except Exception:
                name = "Unknown"
            sections.append({
                "name": name,
                "virtual_size": section.Misc_VirtualSize,
                "raw_size": section.SizeOfRawData,
                "entropy": round(section.get_entropy(), 3),
                "characteristics": f"0x{section.Characteristics:08X}",
            })

        # Imports
        imports = []
        suspicious_imports_list = []
        SUSPICIOUS_APIS = {
            "VirtualAlloc", "VirtualProtect", "CreateRemoteThread",
            "WriteProcessMemory", "ReadProcessMemory", "OpenProcess",
            "NtUnmapViewOfSection", "IsDebuggerPresent", "CreateToolhelp32Snapshot",
            "SetWindowsHookEx", "GetAsyncKeyState", "RegSetValueEx",
            "URLDownloadToFile", "WinExec", "ShellExecute",
        }

        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                try:
                    dll_name = entry.dll.decode("utf-8", errors="replace")
                except Exception:
                    dll_name = "Unknown"

                funcs = []
                for imp in entry.imports[:20]:
                    if imp.name:
                        fname = imp.name.decode("utf-8", errors="replace")
                        funcs.append(fname)
                        if fname in SUSPICIOUS_APIS:
                            suspicious_imports_list.append(f"{dll_name}!{fname}")

                imports.append({
                    "dll": dll_name,
                    "functions": funcs[:10],
                    "count": len(entry.imports),
                })

        # Subsystem
        subsystem_map = {
            0: "Unknown", 1: "Native", 2: "Windows GUI",
            3: "Windows Console", 5: "OS/2 Console",
            7: "POSIX Console", 9: "Windows CE",
        }
        subsystem = subsystem_map.get(
            pe.OPTIONAL_HEADER.Subsystem,
            f"0x{pe.OPTIONAL_HEADER.Subsystem:02X}",
        )

        # Heuristic packing check
        high_entropy_sections = sum(
            1 for s in sections if s["entropy"] > 7.0
        )
        is_packed = high_entropy_sections > 0 and len(imports) <= 2

        pe.close()

        return {
            "is_pe": True,
            "machine": machine,
            "compile_time": compile_time,
            "sections": sections,
            "imports": imports[:15],
            "entry_point": f"0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08X}",
            "image_base": f"0x{pe.OPTIONAL_HEADER.ImageBase:016X}",
            "subsystem": subsystem,
            "is_dll": bool(pe.FILE_HEADER.Characteristics & 0x2000),
            "is_packed": is_packed,
            "suspicious_imports": suspicious_imports_list,
        }

    def analyze(self, file_path: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.extract(file_path)

    def health_check(self) -> dict[str, Any]:
        try:
            import pefile
            return {"service": "PE Metadata Service", "status": "Healthy", "pefile_version": pefile.__version__}
        except ImportError:
            return {"service": "PE Metadata Service", "status": "Degraded", "note": "pefile not installed"}


pe_metadata_service = PEMetadataService()
