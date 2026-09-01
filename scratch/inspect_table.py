import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.db import db
cols = db.fetchall("PRAGMA table_info(scan_history)")
print("Columns in scan_history:")
for c in cols:
    print(dict(c))
