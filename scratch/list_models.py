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

print("--- 1. Listing Groq models ---")
r_groq = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {groq_key}"})
print(f"Groq status: {r_groq.status_code}")
if r_groq.status_code == 200:
    models = [m["id"] for m in r_groq.json().get("data", [])]
    print(f"Groq active models: {models[:10]}")
else:
    print(f"Groq list error: {r_groq.text}")

print("\n--- 2. Listing NVIDIA models ---")
r_nim = requests.get("https://integrate.api.nvidia.com/v1/models", headers={"Authorization": f"Bearer {nvidia_key}"})
print(f"NVIDIA status: {r_nim.status_code}")
if r_nim.status_code == 200:
    models = [m["id"] for m in r_nim.json().get("data", [])]
    print(f"NVIDIA active models: {models[:10]}")
else:
    print(f"NVIDIA list error: {r_nim.text}")

print("\n--- 3. Listing Gemini models ---")
r_gem = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}")
print(f"Gemini status: {r_gem.status_code}")
if r_gem.status_code == 200:
    models = [m["name"] for m in r_gem.json().get("models", [])]
    print(f"Gemini active models: {models[:10]}")
else:
    print(f"Gemini list error: {r_gem.text}")
