"""
===========================================================
CyberMind AI
Database Migration
===========================================================
"""

from database.db import db
from database.schema import SCHEMA


INDEXES = [

    """
    CREATE INDEX IF NOT EXISTS idx_scan_type
    ON scan_history(scan_type);
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_scan_time
    ON scan_history(scan_time);
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_url
    ON url_scans(url);
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_domain
    ON domain_scans(domain);
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_email
    ON email_scans(email);
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_ip
    ON ip_scans(ip);
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_sha256
    ON file_scans(sha256);
    """
]


DEFAULT_SETTINGS = [

    ("theme", "dark"),

    ("language", "English"),

    ("database_version", "1.0.0"),

    ("auto_backup", "True"),

    ("backup_interval", "7"),

    ("report_format", "pdf"),

    ("max_scan_history", "10000")

]


def create_tables():
    """
    Create All Tables
    """

    for query in SCHEMA:

        db.execute(query)

    print("Tables Created")


def create_indexes():
    """
    Create All Indexes
    """

    for query in INDEXES:

        db.execute(query)

    print("Indexes Created")


def insert_default_settings():
    """
    Insert Default Settings
    """

    query = """
    INSERT OR IGNORE INTO settings
    (
        key,
        value
    )
    VALUES
    (
        ?,
        ?
    )
    """

    db.executemany(
        query,
        DEFAULT_SETTINGS
    )

    print("Default Settings Added")


def run_custom_migrations():
    """
    Run table alteration migrations if needed.
    """
    # Check scan_history columns
    columns = [row["name"] for row in db.fetchall("PRAGMA table_info(scan_history)")]
    if "country" not in columns:
        print("Migrating scan_history: adding country columns...")
        try:
            db.execute("ALTER TABLE scan_history ADD COLUMN country TEXT;")
            db.execute("ALTER TABLE scan_history ADD COLUMN country_code TEXT;")
            db.execute("ALTER TABLE scan_history ADD COLUMN latitude REAL;")
            db.execute("ALTER TABLE scan_history ADD COLUMN longitude REAL;")
            print("scan_history migration completed successfully.")
        except Exception as e:
            print(f"Error during scan_history migration: {e}")


def migrate():
    """
    Initialize Database
    """

    db.connect()

    create_tables()

    run_custom_migrations()

    create_indexes()

    insert_default_settings()

    db.close()

    print("Database Ready")


if __name__ == "__main__":

    migrate()