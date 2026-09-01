import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.llm_router import llm_router

messages = [
    {"role": "system", "content": "You are a cyber reasoning system. Return valid JSON only."},
    {"role": "user", "content": "Analyze SQL injection. Return JSON: {\"is_real_vulnerability\": true, \"root_cause\": \"direct sql concat\", \"exploit_payload_example\": \"' OR 1=1 --\"}"}
]

print("Testing llm_router.query()...")
t0 = time.time()
res = llm_router.query(messages, task_type="reasoning")
print(f"Time: {round(time.time()-t0, 2)}s")
print(f"Success: {res.get('success')}")
print(f"Provider: {res.get('provider_name')}")
print(f"Content: {res.get('content')[:200]}")
