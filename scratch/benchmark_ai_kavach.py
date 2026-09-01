import io
import os
import sys
import time
import zipfile
import psutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.code_scanner import CodeSecurityScanner
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator
from modules.autonomous_crs.llm_router import llm_router

# ── BENCHMARK TEST SUITE: 4 REAL PROJECT VULNERABILITY ARCHIVES ──

BENCHMARK_PROJECTS = {
    "MediMind-AI (CWE-502)": {
        "cwe": "CWE-502",
        "file": "verify_ml_model.py",
        "code": """import pickle
import os

def verify_model(model_path):
    # Insecure Deserialization in ML Pipeline
    with open(model_path, "rb") as f:
        payload = pickle.load(f)
    model = payload.get("model")
    return model
"""
    },
    "AuthGuard-Service (CWE-89)": {
        "cwe": "CWE-89",
        "file": "auth_service.py",
        "code": """import sqlite3

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL Injection via string formatting
    query = f"SELECT id, role FROM accounts WHERE user = '{username}' AND pass = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user
"""
    },
    "NetDiagnostic-Tool (CWE-78)": {
        "cwe": "CWE-78",
        "file": "network_diagnostics.py",
        "code": """import os
import subprocess

def ping_host(host_address):
    # Command Injection via unsanitized shell call
    cmd = f"ping -c 1 {host_address}"
    res = os.system(cmd)
    return res
"""
    },
    "DocViewer-Portal (CWE-22)": {
        "cwe": "CWE-22",
        "file": "doc_viewer.py",
        "code": """import os

def read_user_document(doc_filename):
    base_dir = "/var/www/uploads"
    # Path Traversal via unvalidated path joining
    filepath = os.path.join(base_dir, doc_filename)
    with open(filepath, "r") as f:
        content = f.read()
    return content
"""
    }
}


def run_comprehensive_benchmark():
    process = psutil.Process(os.getpid())
    scanner = CodeSecurityScanner()
    orchestrator = AutonomousCRSOrchestrator(use_offline_mode=False)

    print("=" * 70)
    print("CYBERMIND AI — AI KAVACH HACKATHON BENCHMARK & HARDENING SUITE")
    print("=" * 70)

    results_summary = []

    for name, data in BENCHMARK_PROJECTS.items():
        print(f"\n[BENCHMARK] Testing Project: {name}")
        cwe_target = data["cwe"]
        filename = data["file"]
        code = data["code"]

        mem_before = process.memory_info().rss / (1024 * 1024)
        t_start = time.time()

        # Step 1: Static Discovery
        scan_res = scanner.scan_code_string(code, filename=filename)
        findings = scan_res.get("findings", [])
        found_cwe = any(cwe_target in f.get("cwe", "") for f in findings)

        # Step 2: Full Autonomous Lifecycle
        pipe_res = orchestrator.run_pipeline(code, filename=filename)
        t_end = time.time()
        mem_after = process.memory_info().rss / (1024 * 1024)

        duration = round(t_end - t_start, 2)
        mem_used = round(mem_after - mem_before, 2)

        reproduced = pipe_res.get("reproduction", {}).get("reproduced", False)
        syntax_valid = pipe_res.get("patch", {}).get("syntax_valid", False)
        tests_passed = pipe_res.get("regression", {}).get("tests_passed", 0)
        tests_run = pipe_res.get("regression", {}).get("tests_run", 0)
        refuzz_inputs = pipe_res.get("regression", {}).get("refuzz_inputs_tested", 0)
        refuzz_crashes = pipe_res.get("regression", {}).get("refuzz_crashes", 0)
        verified = pipe_res.get("verification", {}).get("verified", False)
        cert_id = pipe_res.get("verification", {}).get("verification_certificate_id", "N/A")
        evidence_size = len(pipe_res.get("evidence_zip_bytes", b""))

        print(f"  + SAST Detection: {'PASS' if found_cwe else 'FAIL'} ({len(findings)} findings)")
        print(f"  + Sandbox PoC Reproduction: {'CONFIRMED' if reproduced else 'FAIL'}")
        print(f"  + AI Patch AST Syntax: {'VALID' if syntax_valid else 'SYNTAX_ERROR'}")
        print(f"  + Security Regression: {tests_passed}/{tests_run} Passed")
        print(f"  + Post-Patch Re-Fuzz: {refuzz_inputs} inputs tested, {refuzz_crashes} crashes")
        print(f"  + Fix Verified: {'YES' if verified else 'NO'} [{cert_id}]")
        print(f"  + Execution Time: {duration}s | Mem Delta: {mem_used}MB | Evidence Zip: {evidence_size} bytes")

        results_summary.append({
            "project": name,
            "cwe": cwe_target,
            "detected": found_cwe,
            "reproduced": reproduced,
            "patched": syntax_valid,
            "regression_rate": f"{tests_passed}/{tests_run}",
            "refuzz_inputs": refuzz_inputs,
            "refuzz_crashes": refuzz_crashes,
            "verified": verified,
            "cert_id": cert_id,
            "time_sec": duration
        })

    # Repeatability Run: Test MediMind-AI 3 times consecutively
    print("\n" + "=" * 70)
    print("REPEATABILITY & RELIABILITY TEST (MediMind-AI x 3 Consecutive Runs)")
    print("=" * 70)
    repeat_times = []
    medimind_code = BENCHMARK_PROJECTS["MediMind-AI (CWE-502)"]["code"]
    for i in range(1, 4):
        t0 = time.time()
        r = orchestrator.run_pipeline(medimind_code, filename="verify_ml_model.py")
        dt = round(time.time() - t0, 2)
        repeat_times.append(dt)
        ver = r.get("verification", {}).get("verified")
        print(f"  Run #{i}: Status={'VERIFIED' if ver else 'FAILED'} in {dt}s (Cert: {r.get('verification',{}).get('verification_certificate_id')})")

    avg_time = round(sum(repeat_times) / len(repeat_times), 2)
    print(f"  Mean Execution Latency: {avg_time}s across 3 runs")

    return results_summary


if __name__ == "__main__":
    summary = run_comprehensive_benchmark()
