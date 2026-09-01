import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.fuzzing_engine import FuzzingEngine

f = FuzzingEngine()
patched_code = """
import json

def verify_model(model_path):
    with open(model_path, 'r') as f:
        return json.load(f)
"""

res = f.run_fuzz_campaign(patched_code, cwe_type="CWE-502", iterations=35)
print("Fuzz Result:")
print("inputs_tested:", res.get("inputs_tested"))
print("total_crashes:", res.get("total_crashes"))
print("crashes detail:", res.get("crashes"))
