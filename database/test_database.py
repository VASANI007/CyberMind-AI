"""
===========================================================
CyberMind AI
Database Health Check
===========================================================
"""

from database.db import db
from config.settings import DATABASE_PATH


TABLES = [

    "users",

    "scan_history",

    "url_scans",

    "website_scans",

    "domain_scans",

    "email_scans",

    "ip_scans",

    "file_scans",

    "qr_scans",

    "api_logs",

    "reports",

    "settings",

    "scan_statistics"

]


def check_database():

    print("\n====================================")
    print("CyberMind AI Database Health Check")
    print("====================================\n")

    # Database Exists

    if DATABASE_PATH.exists():

        print("[PASS] Database File Found")

    else:

        print("[FAIL] Database File Not Found")

        return

    # Connection

    try:

        db.connect()

        print("[PASS] Database Connected")

    except Exception as error:

        print(f"[FAIL] Connection Error : {error}")

        return

    # Tables

    print("\nChecking Tables\n")

    for table in TABLES:

        query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?;
        """

        result = db.fetchone(
            query,
            (table,)
        )

        if result:

            print(f"[PASS] {table}")

        else:

            print(f"[FAIL] {table}")

    # Insert Test

    print("\nTesting Insert\n")

    try:

        db.execute(
            """
            INSERT INTO users
            (
                name,
                email
            )
            VALUES
            (
                ?,
                ?
            );
            """,
            (
                "Test User",
                "test@cybermind.ai"
            )
        )

        print("[PASS] Insert")

    except Exception as error:

        print(f"[FAIL] Insert : {error}")

    # Read Test

    print("\nTesting Read\n")

    result = db.fetchone(
        """
        SELECT *
        FROM users
        WHERE email=?;
        """,
        (
            "test@cybermind.ai",
        )
    )

    if result:

        print("[PASS] Read")

    else:

        print("[FAIL] Read")

    # Delete Test

    print("\nTesting Delete\n")

    db.execute(
        """
        DELETE FROM users
        WHERE email=?;
        """,
        (
            "test@cybermind.ai",
        )
    )

    print("[PASS] Delete")

    db.close()

    print("\n====================================")
    print("Database Test Completed")
    print("====================================")


if __name__ == "__main__":

    check_database()