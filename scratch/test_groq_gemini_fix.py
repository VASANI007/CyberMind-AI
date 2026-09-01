import os
import requests
from dotenv import load_dotenv
load_dotenv(".env")

# 1. Test Groq with llama-3.3-70b-versatile and llama-3.1-8b-instant
groq_key = os.environ.get("GROQ_API_KEY")
print("GROQ KEY exists:", bool(groq_key))
for m in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "groq/compound"]:
    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 10},
        timeout=5
    )
    print(f"Groq ({m}): status={res.status_code}, response={res.text[:80]}")

# 2. Test Gemini with single combined user prompt
gemini_key = os.environ.get("GEMINI_API_KEY")
print("\nGEMINI KEY exists:", bool(gemini_key))
res = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}",
    json={"contents": [{"role": "user", "parts": [{"text": "Hi"}]}], "generationConfig": {"maxOutputTokens": 10}},
    timeout=5
)
print(f"Gemini 2.5-flash: status={res.status_code}, response={res.text[:80]}")

res = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
    json={"contents": [{"role": "user", "parts": [{"text": "Hi"}]}], "generationConfig": {"maxOutputTokens": 10}},
    timeout=5
)
print(f"Gemini 1.5-flash: status={res.status_code}, response={res.text[:80]}")
