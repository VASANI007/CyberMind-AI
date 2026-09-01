import os
import requests
from dotenv import load_dotenv
load_dotenv(".env")

gemini_key = os.environ.get("GEMINI_API_KEY")
res = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={gemini_key}",
    json={"contents": [{"role": "user", "parts": [{"text": "Return json: {\"status\": \"ok\"}"}]}], "generationConfig": {"maxOutputTokens": 50}},
    timeout=5
)
print(f"Gemini 3.6-flash: status={res.status_code}, response={res.text[:120]}")

groq_key = os.environ.get("GROQ_API_KEY")
res = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
    json={"model": "groq/compound", "messages": [{"role": "user", "content": "Return json: {\"status\": \"ok\"}"}], "max_tokens": 50},
    timeout=5
)
print(f"Groq compound: status={res.status_code}, response={res.text[:120]}")
