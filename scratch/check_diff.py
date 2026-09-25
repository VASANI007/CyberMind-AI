import sys, subprocess
sys.stdout.reconfigure(encoding="utf-8")
diff = subprocess.check_output(["git", "diff", "HEAD", "app.py"], text=True, encoding="utf-8", errors="replace")
for line in diff.splitlines():
    if any(k in line for k in ['"icon":', 'MAIN_MENU', 'SCANNERS_DISPLAY']):
        print(line)
