import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Test Groq with models
groq_key = os.environ.get("GROQ_API_KEY")
print("=== 1. Checking Groq Models ===")
groq_models = ["llama-3.1-8b-instant", "llama-3.3-70b-specdec", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it", "llama3-8b-8192"]
for m in groq_models:
    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 10},
        timeout=8
    )
    print(f"Groq [{m}]: {res.status_code}")
    if res.status_code == 200:
        print(f"  -> SUCCESS! Response: {res.json()['choices'][0]['message']['content'].strip()}")
        break

# 2. Test NVIDIA NIM models
nvidia_key = os.environ.get("NVIDIA_API_KEY")
print("\n=== 2. Checking NVIDIA NIM Models ===")
nim_models = ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-8b-instruct", "nvidia/llama-3.1-nemotron-70b-instruct", "deepseek-ai/deepseek-r1", "mistralai/mistral-large-2-instruct"]
for m in nim_models:
    res = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 10},
        timeout=8
    )
    print(f"NVIDIA NIM [{m}]: {res.status_code}")
    if res.status_code == 200:
        print(f"  -> SUCCESS! Response: {res.json()['choices'][0]['message']['content'].strip()}")
        break

# 3. Test Gemini Models
gemini_key = os.environ.get("GEMINI_API_KEY")
print("\n=== 3. Checking Gemini API ===")
for m in ["gemini-1.5-flash-latest", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
    res = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": "Hi"}]}]},
        timeout=8
    )
    print(f"Gemini [{m}]: {res.status_code} - {res.text[:120]}")
    if res.status_code == 200:
        break
