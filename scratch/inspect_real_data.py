import sqlite3
import json
from pathlib import Path

# 1. Database stats
db_path = Path('database/cybermind.db')
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]
    print(f"Total DB Tables: {len(tables)}")
    print(f"Tables: {', '.join(tables)}")
    
    cursor.execute("SELECT COUNT(*) FROM scan_history;")
    total_scans = cursor.fetchone()[0]
    print(f"Total Scans in scan_history: {total_scans}")
    
    cursor.execute("SELECT scan_type, COUNT(*) FROM scan_history GROUP BY scan_type;")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} scans")

    cursor.execute("SELECT risk_level, COUNT(*) FROM scan_history GROUP BY risk_level;")
    print("Risk levels:", cursor.fetchall())
    conn.close()

# 2. ML Metrics
metrics_path = Path('ml/models/cybermind_metrics.json')
if metrics_path.exists():
    with open(metrics_path, encoding='utf-8') as f:
        m = json.load(f)
        print("\nML Metrics:")
        print(json.dumps(m, indent=2))
