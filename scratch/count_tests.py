import subprocess
import time

t0 = time.time()
res = subprocess.run(["pytest", "--collect-only", "-q"], capture_output=True, text=True)
t1 = time.time()
print(res.stdout[-300:])
print(f"Collection time: {t1-t0:.2f}s")
