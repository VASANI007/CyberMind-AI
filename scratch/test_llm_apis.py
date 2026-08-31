import os
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

test_prompt = [{"role": "user", "content": "Reply with only the word: ONLINE_OK"}]

print("=" * 60)
print("[*] TESTING CYBERMIND AI LLM API CONNECTIONS")
print("=" * 60)

# 1. Groq Test
groq_key = llm_router.get_api_key("GROQ")
print(f"\n1. 🔵 Groq LPU API: (Key: {groq_key[:10]}... if configured)")
try:
    groq_res = llm_router._call_groq(groq_key, test_prompt, temp=0.1, tokens=50)
    if "ONLINE_OK" in groq_res or len(groq_res) > 0 and not groq_res.startswith("Error"):
        print(f"   Status: ✅ WORKING (Response: {groq_res.strip()})")
    else:
        print(f"   Status: ❌ FAILED ({groq_res})")
except Exception as e:
    print(f"   Status: ❌ EXCEPTION ({e})")

# 2. NVIDIA NIM Test
nvidia_key = llm_router.get_api_key("NVIDIA_NIM")
print(f"\n2. 🟠 NVIDIA NIM API: (Key: {nvidia_key[:10]}... if configured)")
try:
    nim_res = llm_router._call_nvidia_nim(nvidia_key, test_prompt, temp=0.1, tokens=50)
    if "ONLINE_OK" in nim_res or len(nim_res) > 0 and not nim_res.startswith("Error"):
        print(f"   Status: ✅ WORKING (Response: {nim_res.strip()})")
    else:
        print(f"   Status: ❌ FAILED ({nim_res})")
except Exception as e:
    print(f"   Status: ❌ EXCEPTION ({e})")

# 3. Google Gemini Test
gemini_key = llm_router.get_api_key("GEMINI")
print(f"\n3. 🟢 Google Gemini API: (Key: {gemini_key[:10]}... if configured)")
try:
    gemini_res = llm_router._call_gemini(gemini_key, test_prompt, temp=0.1, tokens=50)
    if "ONLINE_OK" in gemini_res or len(gemini_res) > 0 and not gemini_res.startswith("Error"):
        print(f"   Status: ✅ WORKING (Response: {gemini_res.strip()})")
    else:
        print(f"   Status: ❌ FAILED ({gemini_res})")
except Exception as e:
    print(f"   Status: ❌ EXCEPTION ({e})")

print("\n" + "=" * 60)
