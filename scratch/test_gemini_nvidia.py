import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

gemini_key = os.environ.get("GEMINI_API_KEY")
nvidia_key = os.environ.get("NVIDIA_API_KEY")

print("--- Testing Gemini gemini-3.6-flash & variants ---")
for m in ["gemini-3.6-flash", "gemini-flash-latest", "gemini-3.6-pro", "gemini-3.0-flash"]:
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": "Reply with GEMINI_ONLINE"}]}]},
        timeout=10
    )
    print(f"Gemini [{m}]: {r.status_code}")
    if r.status_code == 200:
        text = r.json()['candidates'][0]['content']['parts'][0]['text']
        print(f"  -> SUCCESS! Response: {text.strip()}")
        break

print("\n--- Testing NVIDIA NIM models ---")
for m in ["deepseek-ai/deepseek-v4-flash-0731", "deepseek-ai/deepseek-v4-pro-0813", "01-ai/yi-large", "ai21labs/jamba-1.5-large-instruct", "google/codegemma-1.1-7b"]:
    r = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": "Reply with NVIDIA_ONLINE"}], "max_tokens": 50},
        timeout=10
    )
    print(f"NVIDIA NIM [{m}]: {r.status_code}")
    if r.status_code == 200:
        print(f"  -> SUCCESS! Response: {r.json()['choices'][0]['message']['content'].strip()}")
        break
