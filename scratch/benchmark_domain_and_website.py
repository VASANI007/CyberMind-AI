import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from dotenv import load_dotenv
load_dotenv(".env")

from modules.domain_scanner import domain_scanner
from modules.website_scanner import website_scanner

test_target = "example.com"
test_url = "https://example.com"

print("--- DOMAIN SCANNER ---")
t0 = time.time()
res_dom = domain_scanner.analyze(test_target)
print(f"Domain scan completed in: {time.time() - t0:.2f}s | Success: {res_dom.get('success')}")

print("--- WEBSITE SCANNER ---")
t1 = time.time()
res_web = website_scanner.analyze(test_url)
print(f"Website scan completed in: {time.time() - t1:.2f}s | Success: {res_web.get('success')}")
