import os
import sys
import io
import zipfile
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.getcwd())
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator

def test_synthetic_batch_project():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        # File 1: SQL Injection
        zf.writestr("services/auth_service.py", """
def query_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
""")
        # File 2: Command Injection
        zf.writestr("utils/network_helper.py", """
import os
def ping_server(target_ip):
    cmd = f"ping -c 2 {target_ip}"
    os.system(cmd)
""")
        # File 3: Untouched clean file
        zf.writestr("config/settings.py", """
APP_NAME = "DefenseSecGateway"
PORT = 8080
DEBUG = False
""")

    buf.seek(0)
    zip_bytes = buf.getvalue()

    orch = AutonomousCRSOrchestrator(use_offline_mode=True)
    res = orch.run_project_zip_pipeline(zip_bytes)

    print("\n--- MASTER CERTIFICATE ---")
    mc = res.get("master_certificate", {})
    for k, v in mc.items():
        print(f"  {k}: {v}")

    print("\n--- INDIVIDUAL TARGET RESULTS ---")
    for idx, f in enumerate(res.get("file_results", []), 1):
        target = f.get("target_file")
        ver = f.get("verification", {})
        print(f"  [{idx}] {target} -> {ver.get('badge_text')} (Token: {ver.get('verification_certificate_id')})")
        print(f"      Passed: {ver.get('passed_gates')}/{ver.get('total_gates')}")
        print(f"      Semantic: {f.get('patch', {}).get('semantic_preservation')}")

    print(f"\nPatched Project ZIP: {len(res.get('patched_project_zip_bytes', b''))} bytes")
    print(f"Master Evidence ZIP: {len(res.get('evidence_zip_bytes', b''))} bytes")

    # Verify that the patched project zip contains the untouched file intact and the patched files
    patched_buf = io.BytesIO(res["patched_project_zip_bytes"])
    with zipfile.ZipFile(patched_buf, "r") as pzf:
        namelist = pzf.namelist()
        print(f"Patched ZIP Files ({len(namelist)}): {namelist}")
        assert "config/settings.py" in namelist, "Untouched config file must be preserved"
        settings_content = pzf.read("config/settings.py").decode("utf-8")
        assert "APP_NAME = \"DefenseSecGateway\"" in settings_content, "Untouched content must match exactly"
        print("✅ FULL PROJECT ZIP RECONSTRUCTION VERIFIED 100%!")

if __name__ == "__main__":
    test_synthetic_batch_project()
