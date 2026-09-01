import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

nvidia_key = os.environ.get("NVIDIA_API_KEY")

nim_test_models = [
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "meta/llama-3.1-8b-instruct",
    "meta/llama3-70b-instruct",
    "mistralai/mixtral-8x7b-instruct-v0.1",
    "01-ai/yi-large",
    "ai21labs/jamba-1.5-large-instruct",
    "deepseek-ai/deepseek-v4-flash-0731"
]

print("--- Testing NVIDIA NIM Models with 20s timeout ---")
for m in nim_test_models:
    try:
        r = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"},
            json={"model": m, "messages": [{"role": "user", "content": "Respond with: OK"}], "max_tokens": 20},
            timeout=20
        )
        print(f"[{m}]: HTTP {r.status_code}")
        if r.status_code == 200:
            print(f"  -> SUCCESS! Response: {r.json()['choices'][0]['message']['content'].strip()[:80]}")
            break
        else:
            print(f"  -> Detail: {r.text[:120]}")
    except Exception as e:
        print(f"[{m}]: Timeout / Exception: {e}")
