import io
import os
import sys
import zipfile
import json
import time

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.getcwd())
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator

print("=" * 60)
print("TEST 1: NEGATIVE TEST (Clean Python Project with Zero Vulnerabilities)")
print("=" * 60)

clean_zip_buf = io.BytesIO()
with zipfile.ZipFile(clean_zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("my_clean_app/main.py", 'def add(a, b):\n    return a + b\n\nif __name__ == "__main__":\n    print(add(2, 3))\n')
    zf.writestr("my_clean_app/utils.py", 'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n')
    zf.writestr("my_clean_app/config.json", '{"version": "1.0.0", "status": "secure"}')

clean_zip_bytes = clean_zip_buf.getvalue()
orch = AutonomousCRSOrchestrator(use_offline_mode=True)
clean_res = orch.run_project_zip_pipeline(zip_bytes=clean_zip_bytes)

print("Clean Project Result:")
print("  Total Files:", clean_res["project_overview"]["total_files"])
print("  Candidate Findings:", len(clean_res["project_overview"]["findings"]))
print("  Target Files to Repair:", len(clean_res["file_results"]))
print("  Verdict:", clean_res["master_certificate"]["status"])
assert len(clean_res["file_results"]) == 0, "Clean project must have 0 repair targets!"
assert clean_res["project_overview"]["total_files"] == 3, "Must discover all 3 files!"
print("[OK] TEST 1 (Clean Project) PASSED 100%!\n")

print("=" * 60)
print("TEST 2: ARBITRARY UNSEEN MULTI-CWE SYNTHETIC PROJECT")
print("=" * 60)

unseen_zip_buf = io.BytesIO()
with zipfile.ZipFile(unseen_zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. Arbitrary CWE-89 SQLi
    zf.writestr("military_c2/database/db_driver.py", '''
import sqlite3
def fetch_telemetry(sensor_id_param):
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    query = f"SELECT * FROM telemetry WHERE sensor = '{sensor_id_param}'"
    cur.execute(query)
    return cur.fetchall()
''')
    # 2. Arbitrary CWE-78 Command Injection
    zf.writestr("military_c2/net/ping_gateway.py", '''
import os
import subprocess
def ping_node(ip_target):
    cmd = f"ping -c 1 {ip_target}"
    os.system(cmd)
''')
    # 3. Arbitrary CWE-95 Code Injection (eval)
    zf.writestr("military_c2/evaluator/math_engine.py", '''
def compute_formula(user_expression):
    return eval(user_expression)
''')
    # 4. Arbitrary CWE-327 Broken Crypto
    zf.writestr("military_c2/crypto/auth_hasher.py", '''
import hashlib
def generate_legacy_token(credential_secret):
    return hashlib.md5(credential_secret.encode('utf-8')).hexdigest()
''')
    # 5. Untouched files
    zf.writestr("military_c2/config/tactical.json", '{"c2_channel": "ALPHA-7", "frequency": 433.92}')
    zf.writestr("military_c2/README.md", '# Tactical C2 Gateway\nClassified Military Infrastructure.\n')

unseen_bytes = unseen_zip_buf.getvalue()
t0 = time.time()
unseen_res = orch.run_project_zip_pipeline(zip_bytes=unseen_bytes)
duration = time.time() - t0

cert = unseen_res["master_certificate"]
print(f"Unseen Multi-CWE Project Result (Duration: {duration:.2f}s):")
print("  Total Files Discovered:", cert["total_files"])
print("  Candidate Findings:", cert["candidate_findings_count"])
print("  Target Files to Repair:", cert["target_files_count"])
print("  Verified Fixes:", cert["verified_count"])
print("  Pending:", cert["pending_count"])
print("  Failed:", cert["failed_count"])
print("  Master Badge:", cert["master_badge"])

# Check reconstructed zip
patched_zip_bytes = unseen_res.get("patched_zip_bytes", b"")
with zipfile.ZipFile(io.BytesIO(patched_zip_bytes), "r") as pzf:
    patched_names = pzf.namelist()
    print("  Reconstructed ZIP Files:", patched_names)
    assert "military_c2/config/tactical.json" in patched_names
    assert "military_c2/README.md" in patched_names

print("\nIndividual Target Results:")
for r in unseen_res["file_results"]:
    fn = r["target_file"]
    cwe = r["finding"]["cwe"]
    ver = r["verification"]["badge_text"]
    gates = f"{r['verification']['passed_gates']}/{r['verification']['total_gates']}"
    print(f"  • {fn} ({cwe}) -> {ver} (Gates: {gates})")

assert cert["verified_count"] >= 3, "Must successfully verify dynamic targets!"
print("\n[OK] TEST 2 (Arbitrary Unseen Multi-CWE Project) PASSED 100%!")
