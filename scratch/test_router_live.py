import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env", override=True)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from modules.autonomous_crs.llm_router import llm_router

print("=" * 60)
print("TESTING LLM ROUTER MULTI-PROVIDER PIPELINE")
print("=" * 60)

# Test 1: Static Analysis Task (Routes to Gemini)
print("\n[Task: static_analysis] -> Expected Primary: Gemini")
r1 = llm_router.query([{"role": "user", "content": "Explain what CWE-89 is in 1 short sentence."}], task_type="static_analysis")
print(f"Success: {r1['success']}")
print(f"Provider Used: {r1['provider_name']}")
print(f"Response: {r1['content'].strip()[:140]}...")

# Test 2: Fuzzing Task (Routes to Groq)
print("\n[Task: fuzzing] -> Expected Primary: Groq")
r2 = llm_router.query([{"role": "user", "content": "Give 2 common SQL injection payloads."}], task_type="fuzzing")
print(f"Success: {r2['success']}")
print(f"Provider Used: {r2['provider_name']}")
print(f"Response: {r2['content'].strip()[:140]}...")

# Test 3: Reasoning Task (Routes to NVIDIA -> Fallback to Gemini)
print("\n[Task: reasoning] -> Fallback to Gemini if NVIDIA unavailable")
r3 = llm_router.query([{"role": "user", "content": "Explain root cause of command injection in 1 line."}], task_type="reasoning")
print(f"Success: {r3['success']}")
print(f"Provider Used: {r3['provider_name']}")
print(f"Response: {r3['content'].strip()[:140]}...")

print("\n" + "=" * 60)
