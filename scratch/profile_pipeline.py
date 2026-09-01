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

print("PROFILING STEP BY STEP:")
t_start = time.time()

t0 = time.time()
scan_res = orch.scanner.scan_code_string(sample, filename="auth_sqli.py")
top_finding = scan_res["findings"][0]
print(f"1. SAST Scanner: {round(time.time() - t0, 3)}s")

t0 = time.time()
reasoning_res = orch.reasoning_agent.reason_vulnerability(top_finding, sample)
print(f"2. LLM Reasoning Agent: {round(time.time() - t0, 3)}s (Provider: {reasoning_res.get('llm_provider')})")

t0 = time.time()
fuzz_res = orch.fuzzer.run_fuzz_campaign(sample, cwe_type=top_finding["cwe"], iterations=25)
print(f"3. Fuzzing Engine: {round(time.time() - t0, 3)}s")

t0 = time.time()
reproduce_res = orch.reproducer.reproduce(sample, top_finding, reasoning_res)
print(f"4. Sandbox Reproducer: {round(time.time() - t0, 3)}s")

t0 = time.time()
patch_res = orch.patch_engineer.generate_patch(sample, top_finding, reasoning_res)
print(f"5. Patch Engineer: {round(time.time() - t0, 3)}s (Provider: {patch_res.get('llm_provider')})")

t0 = time.time()
regression_res = orch.regression_harness.run_regression_suite(
    unpatched_code=sample,
    patched_code=patch_res.get("patched_code", sample),
    finding=top_finding,
    reasoning_data=reasoning_res
)
print(f"6. Regression Harness: {round(time.time() - t0, 3)}s")

t0 = time.time()
verification_res = orch.verification_engine.verify_fix(
    finding=top_finding,
    reproduce_result=reproduce_res,
    patch_result=patch_res,
    regression_result=regression_res
)
print(f"7. Verification Engine: {round(time.time() - t0, 3)}s")

print(f"\nTOTAL PIPELINE: {round(time.time() - t_start, 3)}s")
