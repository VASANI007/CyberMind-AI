from __future__ import annotations

import io
import json
import zipfile
import hashlib
from typing import Any, Dict, List, Optional


class EvidenceBundler:
    """
    Evidence Collection & Packaging Engine.
    Packages full audit trail, source diffs, exploit logs, regression test suites,
    and verification certificates into a standardized defense evidence bundle (.ZIP).
    Includes non-circular cryptographic SHA-256 manifests.
    """

    @staticmethod
    def compute_sha256(data: bytes | str) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def generate_bundle_zip(
        self,
        finding: Dict[str, Any],
        original_code: str,
        reasoning_data: Dict[str, Any],
        reproduce_data: Dict[str, Any],
        patch_data: Dict[str, Any],
        regression_data: Dict[str, Any],
        verification_data: Dict[str, Any],
        timeline_events: List[Dict[str, Any]]
    ) -> bytes:
        """
        Creates an in-memory ZIP byte buffer containing all evidence artifacts with a non-circular manifest.
        """
        buffer = io.BytesIO()

        finding_bytes = json.dumps(finding, indent=2, default=str).encode("utf-8")
        orig_bytes = original_code.encode("utf-8")
        reasoning_bytes = json.dumps(reasoning_data, indent=2, default=str).encode("utf-8")
        reproduce_bytes = json.dumps(reproduce_data, indent=2, default=str).encode("utf-8")
        patch_bytes = patch_data.get("patched_code", "").encode("utf-8")
        diff_bytes = patch_data.get("diff", "").encode("utf-8")
        test_bytes = regression_data.get("test_code", "").encode("utf-8")
        cert_bytes = json.dumps(verification_data, indent=2, default=str).encode("utf-8")

        timeline_str = "\n".join(
            f"[{e.get('timestamp', '')}] [{e.get('agent', 'SYSTEM')}] {e.get('message', '')}"
            for e in timeline_events
        )
        timeline_bytes = timeline_str.encode("utf-8")

        # Non-circular cryptographic manifest
        manifest = {
            "artifact_manifest_version": "2.0.0-DEFENSE",
            "integrity_algorithm": "SHA-256",
            "component_hashes": {
                "01_finding.json": self.compute_sha256(finding_bytes),
                "02_original_code.py": self.compute_sha256(orig_bytes),
                "03_root_cause_analysis.json": self.compute_sha256(reasoning_bytes),
                "04_vulnerability_reproduction.json": self.compute_sha256(reproduce_bytes),
                "05_patched_code.py": self.compute_sha256(patch_bytes),
                "06_patch.diff": self.compute_sha256(diff_bytes),
                "07_test_security_regression.py": self.compute_sha256(test_bytes),
                "09_verification_certificate.json": self.compute_sha256(cert_bytes),
                "10_audit_timeline.log": self.compute_sha256(timeline_bytes)
            }
        }
        manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("evidence/00_master_manifest.json", manifest_bytes)
            zf.writestr("evidence/01_finding.json", finding_bytes)
            zf.writestr("evidence/02_original_code.py", orig_bytes)
            zf.writestr("evidence/03_root_cause_analysis.json", reasoning_bytes)
            zf.writestr("evidence/04_vulnerability_reproduction.json", reproduce_bytes)
            zf.writestr("evidence/05_patched_code.py", patch_bytes)
            zf.writestr("evidence/06_patch.diff", diff_bytes)
            zf.writestr("evidence/07_test_security_regression.py", test_bytes)
            zf.writestr("evidence/08_refuzz_summary.json", json.dumps(regression_data.get("refuzz_summary", {}), indent=2, default=str))
            zf.writestr("evidence/09_verification_certificate.json", cert_bytes)
            zf.writestr("evidence/10_audit_timeline.log", timeline_bytes)

        buffer.seek(0)
        return buffer.getvalue()

    def generate_full_project_zip(
        self,
        original_zip_bytes: bytes,
        patched_files_dict: Dict[str, str]
    ) -> bytes:
        """
        Creates a complete repaired repository archive (.ZIP) with all patched source files
        overlaid onto the original directory tree while preserving all un-modified files and assets.
        """
        input_buf = io.BytesIO(original_zip_bytes)
        output_buf = io.BytesIO()

        with zipfile.ZipFile(input_buf, "r") as in_zf, zipfile.ZipFile(output_buf, "w", zipfile.ZIP_DEFLATED) as out_zf:
            for item in in_zf.infolist():
                filename = item.filename
                norm_fn = filename.replace("\\", "/")
                matched_patch_key = None
                for pk in patched_files_dict:
                    if norm_fn.endswith(pk) or pk.endswith(norm_fn):
                        matched_patch_key = pk
                        break
                
                if matched_patch_key:
                    out_zf.writestr(item, patched_files_dict[matched_patch_key].encode("utf-8"))
                else:
                    out_zf.writestr(item, in_zf.read(item.filename))

        output_buf.seek(0)
        return output_buf.getvalue()

    def generate_project_evidence_zip(
        self,
        project_overview: Dict[str, Any],
        file_results: List[Dict[str, Any]],
        master_certificate: Dict[str, Any],
        timeline_events: List[Dict[str, Any]],
        original_zip_bytes: Optional[bytes] = None,
        patched_zip_bytes: Optional[bytes] = None
    ) -> bytes:
        """
        Creates a master defense evidence bundle (.ZIP) for an entire multi-file project repair lifecycle,
        including component SHA-256 cryptographic hashes for non-circular verification.
        """
        buffer = io.BytesIO()

        component_hashes = {}
        if original_zip_bytes:
            component_hashes["original_repository_zip_sha256"] = self.compute_sha256(original_zip_bytes)
        if patched_zip_bytes:
            component_hashes["patched_repository_zip_sha256"] = self.compute_sha256(patched_zip_bytes)

        manifest = {
            "evidence_bundle_version": "2.0.0-ENTERPRISE",
            "integrity_algorithm": "SHA-256",
            "repository_integrity": component_hashes,
            "project_name": project_overview.get("project_name", "Target Repository"),
            "total_files_repaired": len(file_results),
            "master_certificate_id": master_certificate.get("master_certificate_id", "CM-PROJ-UNKNOWN")
        }

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("evidence/00_master_manifest.json", json.dumps(manifest, indent=2, default=str))
            zf.writestr("evidence/01_project_inventory.json", json.dumps(project_overview, indent=2, default=str))
            zf.writestr("evidence/02_master_verification_certificate.json", json.dumps(master_certificate, indent=2, default=str))
            
            for idx, res in enumerate(file_results, 1):
                f_name = res.get("target_file", f"file_{idx}").replace("/", "_").replace("\\", "_")
                zf.writestr(f"evidence/patches/{f_name}.patch", res.get("patch", {}).get("diff", ""))
                zf.writestr(f"evidence/patched_sources/{f_name}", res.get("patch", {}).get("patched_code", ""))
                zf.writestr(f"evidence/regression_tests/test_regression_{f_name}.py", res.get("regression", {}).get("test_code", ""))
                zf.writestr(f"evidence/findings/{f_name}_finding.json", json.dumps(res.get("finding", {}), indent=2, default=str))

            timeline_str = "\n".join(
                f"[{e.get('timestamp', '')}] [{e.get('agent', 'SYSTEM')}] {e.get('message', '')}"
                for e in timeline_events
            )
            zf.writestr("evidence/audit_timeline.log", timeline_str)

        buffer.seek(0)
        return buffer.getvalue()
