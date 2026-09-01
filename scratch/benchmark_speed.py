import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator
from modules.autonomous_crs_ui import load_sample_code

sample = load_sample_code("auth_sqli.py")
orch = AutonomousCRSOrchestrator()

print("=" * 60)
print("TESTING FULL PIPELINE SPEED...")
print("=" * 60)
t0 = time.time()
res = orch.run_pipeline(sample, "auth_sqli.py")
t1 = time.time()

print(f"\n[OK] Total Pipeline Execution Time: {round(t1 - t0, 2)} seconds!")
print(f"[OK] Success: {res['success']}")
print(f"[OK] Fix Verification: {res['verification']['verdict']} - {res['verification']['badge_text']}")
