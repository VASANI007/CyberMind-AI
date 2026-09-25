import sqlite3

conn = sqlite3.connect("database/cybermind.db")
cursor = conn.cursor()
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
table_names = [t[0] for t in tables]
print(f"Total tables: {len(table_names)}")
print("Tables:", table_names)

indexes = cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';").fetchall()
print(f"Total indexes: {len(indexes)}")

try:
    scan_count = cursor.execute("SELECT COUNT(*) FROM scan_history").fetchone()[0]
    print(f"Total scan_history records: {scan_count}")
except Exception as e:
    print("scan_history error:", e)

for t in table_names:
    try:
        cnt = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {cnt} rows")
    except Exception as e:
        print(f"  {t}: error {e}")
