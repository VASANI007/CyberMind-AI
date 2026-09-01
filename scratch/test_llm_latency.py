import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.llm_router import llm_router

messages = [{"role": "user", "content": "Return json: {\"status\": \"ok\"}"}]

print("Active Providers:", llm_router.get_active_providers())
for p in ["GROQ", "GEMINI", "NVIDIA_NIM"]:
    t0 = time.time()
    try:
        if p == "GROQ":
            r = llm_router._call_groq(llm_router.get_api_key("GROQ"), messages, 0.4, 200)
        elif p == "GEMINI":
            r = llm_router._call_gemini(llm_router.get_api_key("GEMINI"), messages, 0.4, 200)
        elif p == "NVIDIA_NIM":
            r = llm_router._call_nvidia_nim(llm_router.get_api_key("NVIDIA_NIM"), messages, 0.4, 200)
        print(f"Provider {p}: Success={r.get('success')} in {round(time.time()-t0, 2)}s | Model={r.get('model')}")
    except Exception as e:
        print(f"Provider {p}: Error={e} in {round(time.time()-t0, 2)}s")
