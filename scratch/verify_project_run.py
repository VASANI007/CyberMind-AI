import os
import sys
sys.path.insert(0, os.getcwd())
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator

def test_full_project_zip():
    zip_path = os.path.join(os.path.expanduser("~"), "Music", "CyberMind-AI", "MediMind-AI.zip")
    if not os.path.exists(zip_path):
        # Try local workspace relative
        zip_path = "MediMind-AI.zip"
    
    if not os.path.exists(zip_path):
        print("MediMind-AI.zip not found locally in workspace. Skipping file test.")
        return

    with open(zip_path, "rb") as f:
        zip_bytes = f.read()

    print(f"Ingesting {zip_path} ({len(zip_bytes)} bytes)...")
    orch = AutonomousCRSOrchestrator(use_offline_mode=True)
    res = orch.run_project_zip_pipeline(zip_bytes)

    print("\n--- MASTER PROJECT SUMMARY ---")
    mc = res.get("master_certificate", {})
    for k, v in mc.items():
        print(f"  {k}: {v}")

    print(f"\nFiles Repaired Count: {len(res.get('file_results', []))}")
    for idx, f in enumerate(res.get("file_results", []), 1):
        target = f.get("target_file")
        ver = f.get("verification", {})
        print(f"  File {idx}: {target} -> {ver.get('badge_text')} (Token: {ver.get('verification_certificate_id')})")
        print(f"    Passed Gates: {ver.get('passed_gates')}/{ver.get('total_gates')}")
        print(f"    Semantic Check: {f.get('patch', {}).get('semantic_preservation')}")

    print(f"\nPatched Project ZIP bytes: {len(res.get('patched_project_zip_bytes', b''))}")
    print(f"Evidence Bundle ZIP bytes: {len(res.get('evidence_zip_bytes', b''))}")

if __name__ == "__main__":
    test_full_project_zip()
