import os, requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

for model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": "Explain phishing in 1 sentence."}], "max_tokens": 50}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            print(f"SUCCESS {model}: {r.json()['choices'][0]['message']['content'].strip()}")
            break
        else:
            print(f"FAILED {model}: {r.status_code} {r.text[:80]}")
    except Exception as e:
        print(f"ERROR {model}: {e}")
