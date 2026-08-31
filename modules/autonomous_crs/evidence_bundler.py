from __future__ import annotations

import io
import json
import zipfile
from typing import Any, Dict, List, Optional


class EvidenceBundler:
    """
    Evidence Collection & Packaging Engine.
    Packages full audit trail, source diffs, exploit logs, regression test suites,
    and verification certificates into a standardized defense evidence bundle (.ZIP).
    """

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
        Creates an in-memory ZIP byte buffer containing all evidence artifacts.
        """
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Vulnerability Finding Metadata
            zf.writestr(
                "evidence/01_finding.json",
                json.dumps(finding, indent=2)
            )

            # 2. Original Vulnerable Code
            zf.writestr(
                "evidence/02_original_code.py",
                original_code
            )

            # 3. LLM Cyber Reasoning & Root Cause Analysis
            zf.writestr(
                "evidence/03_root_cause_analysis.json",
                json.dumps(reasoning_data, indent=2)
            )

            # 4. Vulnerability Reproduction & Exploit Output
            zf.writestr(
                "evidence/04_vulnerability_reproduction.json",
                json.dumps(reproduce_data, indent=2)
            )

            # 5. Patched Code
            zf.writestr(
                "evidence/05_patched_code.py",
                patch_data.get("patched_code", "")
            )

            # 6. Unified Git Diff
            zf.writestr(
                "evidence/06_patch.diff",
                patch_data.get("diff", "")
            )

            # 7. Synthesized Regression Test Suite
            zf.writestr(
                "evidence/07_test_security_regression.py",
                regression_data.get("test_code", "")
            )

            # 8. Re-Fuzzing Report
            zf.writestr(
                "evidence/08_refuzz_summary.json",
                json.dumps(regression_data.get("refuzz_summary", {}), indent=2)
            )

            # 9. Verification Certificate
            zf.writestr(
                "evidence/09_verification_certificate.json",
                json.dumps(verification_data, indent=2)
            )

            # 10. Audit Timeline Event Log
            timeline_str = "\n".join(
                f"[{e.get('timestamp', '')}] [{e.get('agent', 'SYSTEM')}] {e.get('message', '')}"
                for e in timeline_events
            )
            zf.writestr(
                "evidence/10_audit_timeline.log",
                timeline_str
            )

        buffer.seek(0)
        return buffer.getvalue()
