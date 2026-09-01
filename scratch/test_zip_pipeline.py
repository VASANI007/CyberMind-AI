import io
import sys
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.code_scanner import CodeSecurityScanner
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator

# Create an in-memory test project ZIP
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("MediMind-AI/requirements.txt", "torch==2.1.0\nnumpy>=1.24\nscikit-learn\n")
    z.writestr("MediMind-AI/verify_ml_model.py", """import pickle

def verify_model(model_path):
    with open(model_path, "rb") as f:
        payload = pickle.load(f)
    return payload
""")
    z.writestr("MediMind-AI/utils/helpers.py", "def format_name(name):\n    return name.strip().title()\n")
    z.writestr("MediMind-AI/tests/test_model.py", "def test_something():\n    assert True\n")

zip_bytes = zip_buffer.getvalue()

scanner = CodeSecurityScanner()
print("1. Scanning ZIP Archive...")
scan_res = scanner.scan_zip(zip_bytes)
print("Project Name:", scan_res.get("project_name"))
print("Files Discovered:", scan_res.get("total_files"), f"({scan_res.get('python_files')} Python, {scan_res.get('other_files')} other)")
print("Dependencies Discovered:", scan_res.get("dependencies"))
print("Test Files:", scan_res.get("test_files"))
print("Total Findings:", scan_res.get("total_findings"))
print("Top Finding:", scan_res["findings"][0]["cwe"], "in", scan_res["findings"][0]["file"])

print("\n2. Executing Autonomous Orchestrator on Top Vulnerable File...")
orch = AutonomousCRSOrchestrator(use_offline_mode=False)
top_file = scan_res["findings"][0]["file"]
code = scan_res["files_dict"][top_file]

pipeline_res = orch.run_pipeline(code, filename=top_file)
print("Pipeline Success:", pipeline_res.get("success"))
print("Vulnerability Reproduced:", pipeline_res["reproduction"]["reproduced"])
print("Regression Tests Passed:", pipeline_res["regression"]["tests_passed"], "/", pipeline_res["regression"]["tests_run"])
print("Refuzz Inputs Tested:", pipeline_res["regression"]["refuzz_inputs_tested"])
print("Decision Badge:", pipeline_res["verification"]["badge_text"])
print("Evidence Bundle Size:", len(pipeline_res["evidence_zip_bytes"]), "bytes")
