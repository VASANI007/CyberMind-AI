import sys
sys.path.insert(0, '.')
from database.db import db
db.connect()
tables = db.fetchall("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
print('Tables found:', len(tables))
for row in tables:
    print(' -', dict(row)['name'])
db.close()
