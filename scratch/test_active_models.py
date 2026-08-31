import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

groq_key = os.environ.get("GROQ_API_KEY")
nvidia_key = os.environ.get("NVIDIA_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY")

print("=" * 60)
print("TESTING LLM APIS WITH ACTIVE 2026 MODELS")
print("=" * 60)

# 1. Groq Test
print("\n1. Groq (groq/compound):")
r1 = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
    json={"model": "groq/compound", "messages": [{"role": "user", "content": "Respond with: GROQ_IS_ONLINE"}], "max_tokens": 50},
    timeout=10
)
if r1.status_code == 200:
    print(f"   [SUCCESS] Status 200 -> {r1.json()['choices'][0]['message']['content'].strip()[:100]}")
else:
    print(f"   [FAILED] Status {r1.status_code} -> {r1.text}")

# 2. NVIDIA NIM Test
print("\n2. NVIDIA NIM (deepseek-ai/deepseek-coder-6.7b-instruct):")
r2 = requests.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"},
    json={"model": "deepseek-ai/deepseek-coder-6.7b-instruct", "messages": [{"role": "user", "content": "Respond with: NVIDIA_NIM_IS_ONLINE"}], "max_tokens": 50},
    timeout=10
)
if r2.status_code == 200:
    print(f"   [SUCCESS] Status 200 -> {r2.json()['choices'][0]['message']['content'].strip()[:100]}")
else:
    print(f"   [FAILED] Status {r2.status_code} -> {r2.text}")

# 3. Gemini Test
print("\n3. Google Gemini (gemini-2.5-flash):")
r3 = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}",
    headers={"Content-Type": "application/json"},
    json={"contents": [{"parts": [{"text": "Respond with: GEMINI_IS_ONLINE"}]}]},
    timeout=10
)
if r3.status_code == 200:
    text = r3.json()['candidates'][0]['content']['parts'][0]['text']
    print(f"   [SUCCESS] Status 200 -> {text.strip()[:100]}")
else:
    print(f"   [FAILED] Status {r3.status_code} -> {r3.text}")

print("\n" + "=" * 60)
