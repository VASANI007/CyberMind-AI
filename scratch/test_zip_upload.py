import io
import sys
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.code_scanner import CodeSecurityScanner

# Create in-memory zip containing multiple vulnerable Python files
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w') as zf:
    zf.writestr("backend/auth.py", "import sqlite3\ndef login(u, p):\n    conn = sqlite3.connect('db.db')\n    query = f\"SELECT * FROM users WHERE user='{u}'\"\n    conn.execute(query)\n")
    zf.writestr("services/runner.py", "import os\ndef ping(ip):\n    os.system('ping ' + ip)\n")
    zf.writestr("safe_module.py", "def add(a, b):\n    return a + b\n")

zip_bytes = zip_buffer.getvalue()

scanner = CodeSecurityScanner()
res = scanner.scan_zip(zip_bytes)

print("=" * 60)
print("ZIP ARCHIVE SCAN RESULT:")
print("=" * 60)
print(f"Files Scanned: {res['files_scanned']}")
print(f"Total Findings: {res['total_findings']}")
print(f"Critical: {res['critical']}")
print(f"High: {res['high']}")
print(f"Files Extracted in map: {list(res['files_dict'].keys())}")
for f in res['findings']:
    print(f"  -> [{f['severity']}] {f['file']}:{f['line']} - {f['name']} ({f['cwe']})")

assert res['files_scanned'] == 3
assert res['total_findings'] >= 2
assert "backend/auth.py" in res['files_dict']
print("\n✅ ALL ZIP SCAN TESTS PASSED!")
