import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs_ui import save_crs_scan_to_history
from database.db import db

# Test saving scan history
save_crs_scan_to_history("Autonomous Security Lab", "military_portal.py (CWE-89)", "Critical", 95.0)
save_crs_scan_to_history("Code SAST & AST", "telemetry.py (1 finding)", "High", 75.0)
save_crs_scan_to_history("Fuzz & Sandbox Hub", "CWE-22 (3 crashes)", "Critical", 95.0)

rows = db.fetchall("SELECT * FROM scan_history ORDER BY scan_id DESC LIMIT 5")
print("=" * 60)
print("RECENT SCAN HISTORY RECORDS IN DATABASE:")
print("=" * 60)
for r in rows:
    print(f"Scan ID: {r['scan_id']} | Type: {r['scan_type']} | Target: {r['target']} | Level: {r['risk_level']} | Score: {r['risk_score']}")

assert any(r['scan_type'] == "Autonomous Security Lab" for r in rows)
assert any(r['scan_type'] == "Code SAST & AST" for r in rows)
assert any(r['scan_type'] == "Fuzz & Sandbox Hub" for r in rows)
print("\nALL 3 CRS PANELS ARE CORRECTLY LOGGING TO SCAN HISTORY!")
