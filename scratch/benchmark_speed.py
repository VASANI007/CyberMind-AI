import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from dotenv import load_dotenv
load_dotenv(".env")

from modules.url_scanner import url_scanner

test_url = "https://example.com"

print("--- RUN 1 ---")
t0 = time.time()
res1 = url_scanner.analyze(test_url)
print(f"Run 1 completed in: {time.time() - t0:.2f}s")

print("--- RUN 2 ---")
t1 = time.time()
res2 = url_scanner.analyze(test_url)
print(f"Run 2 completed in: {time.time() - t1:.2f}s")
