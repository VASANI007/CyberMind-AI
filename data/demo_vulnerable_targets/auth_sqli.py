"""
Military Access Control & Authentication Gateway
Vulnerability: CWE-89 (SQL Injection)
"""
import sqlite3
import sys

def authenticate_user(username: str) -> dict:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, username TEXT, role TEXT, clearance_level TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'commander', 'COMMAND_STAFF', 'TOP_SECRET')")
    cursor.execute("INSERT INTO users VALUES (2, 'operator_alpha', 'FIELD_OPERATOR', 'SECRET')")
    conn.commit()

    # VULNERABLE: Direct f-string interpolation into raw SQL query without parameterization
    query = f"SELECT id, username, role, clearance_level FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"authenticated": True, "user_id": row[0], "username": row[1], "clearance": row[3]}
    return {"authenticated": False, "error": "Access Denied"}

if __name__ == "__main__":
    test_user = sys.argv[1] if len(sys.argv) > 1 else "operator_alpha"
    result = authenticate_user(test_user)
    print(f"Auth Result: {result}")
