"""
CyberMind AI
Database Root Manager
Enterprise Production Version
"""

from __future__ import annotations
import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from pathlib import Path
from typing import Any

from config.settings import DATABASE_PATH
from core.logger import logger

from database.connection import database
from database.db import db
from database.db import initialize_database
from database.models import Base
from database.schema import SCHEMA
from database.backup import create_backup


class DatabaseRoot:
    """
    Enterprise Database Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.database_path = Path(DATABASE_PATH)

        self.sqlite = db

        self.sqlalchemy = database

        self.schema = SCHEMA

        self.models = Base

        self.connected = False

        logger.info(
            "Database Root Initialized."
        )

    def initialize(self) -> None:
        """
        Initialize database layer.
        """

        logger.info(
            "Initializing Database..."
        )

        self.verify_database()

        self.connect_sqlite()

        self.connect_sqlalchemy()

        self.load_models()

        self.load_schema()

        self.run_migration()

        self.verify_tables()

        logger.info(
            "Database Ready."
        )

    def verify_database(self) -> bool:
        """
        Verify database file.
        """

        if self.database_path.exists():

            logger.info(
                "Database File Found."
            )

            return True

        logger.error(
            "Database File Missing."
        )

        return False

    def connect_sqlite(self) -> bool:
        """
        Connect SQLite database.
        """

        try:

            self.sqlite.connect()

            self.connected = True

            logger.info(
                "SQLite Connected."
            )

            return True

        except Exception as error:

            logger.exception(error)

            return False

    def connect_sqlalchemy(self) -> bool:
        """
        Connect SQLAlchemy.
        """

        try:

            if self.sqlalchemy.is_connected():

                logger.info(
                    "SQLAlchemy Connected."
                )

                return True

            logger.error(
                "SQLAlchemy Connection Failed."
            )

            return False

        except Exception as error:

            logger.exception(error)

            return False

    def load_models(self) -> None:
        """
        Load SQLAlchemy models.
        """

        logger.info(
            "Loading Models..."
        )

        _ = self.models

        logger.info(
            "Models Loaded."
        )

    def load_schema(self) -> None:
        """
        Load database schema.
        """

        logger.info(
            "Loading Schema..."
        )

        logger.info(
            "%d Tables Registered.",
            len(self.schema)
        )

    def run_migration(self) -> None:
        """
        Run database migration.
        """

        logger.info(
            "Running Migration..."
        )

        initialize_database()

        logger.info(
            "Migration Completed."
        )

    def verify_tables(self) -> bool:
        """
        Verify all tables.
        """

        try:

            result = self.sqlite.fetchall(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table';
                """
            )

            logger.info(
                "%d Tables Found.",
                len(result)
            )

            return True

        except Exception as error:

            logger.exception(error)

            return False
        
    def create_backup(self) -> bool:
        """
        Create database backup.
        """

        try:

            create_backup()

            logger.info(
                "Database Backup Created."
            )

            return True

        except Exception as error:

            logger.exception(error)

            return False

    def database_size(self) -> int:
        """
        Return database size.
        """

        if self.database_path.exists():

            return self.database_path.stat().st_size

        return 0

    def list_tables(self) -> list[str]:
        """
        Return database tables.
        """

        try:

            rows = self.sqlite.fetchall(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name;
                """
            )

            return [

                row["name"]

                for row

                in rows

            ]

        except Exception:

            return []

    def table_count(self) -> int:
        """
        Total tables.
        """

        return len(
            self.list_tables()
        )

    def database_statistics(self) -> dict[str, Any]:
        """
        Database statistics.
        """

        return {

            "database_file":
                str(self.database_path),

            "database_exists":
                self.database_path.exists(),

            "database_size":
                self.database_size(),

            "tables":
                self.table_count(),

            "schema_tables":
                len(self.schema),

            "sqlite_connected":
                self.connected,

            "sqlalchemy_connected":
                self.sqlalchemy.is_connected()

        }

    def health_check(self) -> dict[str, Any]:
        """
        Database health.
        """

        sqlite_ok = self.connected

        sqlalchemy_ok = (
            self.sqlalchemy.is_connected()
        )

        database_ok = (
            self.database_path.exists()
        )

        tables_ok = (
            self.table_count() > 0
        )
        integrity = self.integrity_check()

        indexes = self.verify_indexes()

        settings = self.verify_default_settings()

        healthy = all(
        [
            sqlite_ok,
            sqlalchemy_ok,
            database_ok,
            tables_ok,
            integrity,
            indexes,
            settings
        ]
        )

        

        return {

            "service": "Database",

            "status":
                "Healthy"
                if healthy
                else "Unhealthy",

            "database":
                database_ok,

            "sqlite":
                sqlite_ok,

            "sqlalchemy":
                sqlalchemy_ok,

            "tables":
                self.table_count(),
                
            "integrity": integrity,

            "indexes": indexes,

            "settings": settings

        }

    def status(self) -> dict[str, Any]:
        """
        Database status.
        """

        return {

            "version":
                self.VERSION,

            "health":
                self.health_check(),

            "statistics":
                self.database_statistics()

        }

    def reload(self) -> None:
        """
        Reload database.
        """

        logger.info(
            "Reloading Database..."
        )

        self.initialize()
        
    def integrity_check(self) -> bool:
        """
        Check database integrity.
        """

        try:

            result = self.sqlite.fetchone(
                "PRAGMA integrity_check;"
            )

            if result:

                value = list(result)[0]

                if str(value).lower() == "ok":

                    logger.info(
                        "Database Integrity OK."
                    )

                    return True

            logger.error(
                "Database Integrity Failed."
            )

            return False

        except Exception as error:

            logger.exception(error)

            return False
        
    def verify_default_settings(self) -> bool:
        """
        Verify default settings.
        """

        try:

            result = self.sqlite.fetchone(
                """
                SELECT COUNT(*)
                FROM settings;
                """
            )

            count = list(result)[0]

            if count > 0:

                logger.info(
                    "Default Settings Verified."
                )

            return True

            logger.warning(
                "Settings Table Empty."
            )

            return False

        except Exception as error:

            logger.exception(error)

            return False
        
    def verify_indexes(self) -> bool:
        """
        Verify database indexes.
        """

        try:

            rows = self.sqlite.fetchall(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='index';
                """
            )

            logger.info(
                "%d Indexes Found.",
                len(rows)
            )

            return len(rows) > 0

        except Exception as error:

            logger.exception(error)

            return False
        
    def auto_repair(self) -> bool:
        """
        Auto repair database.
        """

        logger.info(
            "Running Database Auto Repair..."
        )

        try:

            initialize_database()

            logger.info(
                "Database Repaired."
            )

            return True

        except Exception as error:

            logger.exception(error)

            return False

    def shutdown(self) -> None:
        """
        Shutdown database.
        """

        try:

            self.sqlite.close()

            logger.info(
                "SQLite Connection Closed."
            )

        except Exception as error:

            logger.exception(error)

    def __len__(self) -> int:
        """
        Total tables.
        """

        return self.table_count()

    def __repr__(self) -> str:
        """
        String representation.
        """

        return (

            f"DatabaseRoot("
            f"tables={self.table_count()}, "
            f"version='{self.VERSION}')"

        )


database_root = DatabaseRoot()


if __name__ == "__main__":
    print("=" * 60)
    print("     CyberMind AI - Database Manager")
    print("=" * 60)

    database_root.initialize()

    stats = database_root.database_statistics()
    health = database_root.health_check()

    print(f"\nDatabase File : {stats['database_file']}")
    print(f"File Exists   : {stats['database_exists']}")
    print(f"File Size     : {stats['database_size']:,} bytes")
    print(f"Tables        : {stats['tables']}")
    print(f"SQLite        : {'Connected' if stats['sqlite_connected'] else 'Disconnected'}")
    print(f"SQLAlchemy    : {'Connected' if stats['sqlalchemy_connected'] else 'Disconnected'}")
    print(f"Integrity     : {'OK' if health.get('integrity') else 'FAILED'}")
    print(f"Indexes       : {'OK' if health.get('indexes') else 'FAILED'}")
    print(f"\nOverall Status: {health['status']}")

    print("\nTables in Database:")
    for t in database_root.list_tables():
        print(f"  - {t}")

    print("=" * 60)