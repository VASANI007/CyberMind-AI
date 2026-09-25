import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from dotenv import load_dotenv
load_dotenv(".env")

from modules.url_scanner import url_scanner
from modules.domain_scanner import domain_scanner
from modules.website_scanner import website_scanner
from modules.ip_scanner import ip_scanner
from modules.phone_scanner import phone_scanner

scanners = [
    ("URL Scanner", lambda: url_scanner.analyze("https://google.com")),
    ("Domain Scanner", lambda: domain_scanner.analyze("google.com")),
    ("Website Scanner", lambda: website_scanner.analyze("https://google.com")),
    ("IP Scanner", lambda: ip_scanner.analyze("8.8.8.8")),
    ("Phone Scanner", lambda: phone_scanner.analyze("+14152007986")),
]

print("======================================================")
print("SPEED BENCHMARK ACROSS ALL MAIN SCANNERS")
print("======================================================")
for name, scan_fn in scanners:
    t0 = time.time()
    res = scan_fn()
    elapsed = time.time() - t0
    success = res.get("success", False) if isinstance(res, dict) else False
    print(f"[{'PASS' if success else 'WARN'}] {name:16}: {elapsed:.2f}s (Success: {success})")
print("======================================================")
