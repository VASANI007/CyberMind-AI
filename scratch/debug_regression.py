import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.regression_harness import RegressionHarness

h = RegressionHarness()
finding = {"cwe": "CWE-502", "name": "Pickle Deserialization", "file": "test.py"}
reasoning = {"exploit_payload_example": "b'test'"}
res = h.run_regression_suite("old_code", "new_code", finding, reasoning)
print("Regression Result:")
print("all_passed:", res["all_passed"])
print("tests_passed:", res["tests_passed"])
print("refuzz_crashes:", res["refuzz_crashes"])
print("sandbox_output success:", res["sandbox_output"].get("success"))
print("sandbox_output exit_code:", res["sandbox_output"].get("exit_code"))
print("sandbox_output stderr:", res["sandbox_output"].get("stderr"))
