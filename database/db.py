"""
===========================================================
CyberMind AI
Database Connection Manager
===========================================================
"""

import sqlite3
from pathlib import Path

from config.settings import DATABASE_PATH


class Database:

    def __init__(self):

        self.db_path = Path(DATABASE_PATH)

        self.connection = None

        self.cursor = None

    def connect(self):
        """
        Connect Database
        """

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.cursor.execute(
            "PRAGMA foreign_keys = ON;"
        )

        return self.connection

    def execute(
        self,
        query,
        params=None
    ):
        """
        Execute Query
        """

        if self.connection is None:
            self.connect()

        if params:

            self.cursor.execute(
                query,
                params
            )

        else:

            self.cursor.execute(
                query
            )

        self.connection.commit()

        return self.cursor

    def executemany(
        self,
        query,
        data
    ):
        """
        Execute Multiple Queries
        """

        if self.connection is None:
            self.connect()

        self.cursor.executemany(
            query,
            data
        )

        self.connection.commit()

    def fetchone(
        self,
        query,
        params=None
    ):
        """
        Fetch One Record
        """

        cursor = self.execute(
            query,
            params
        )

        return cursor.fetchone()

    def fetchall(
        self,
        query,
        params=None
    ):
        """
        Fetch All Records
        """

        cursor = self.execute(
            query,
            params
        )

        return cursor.fetchall()

    def commit(self):
        """
        Commit Changes
        """

        if self.connection:

            self.connection.commit()

    def rollback(self):
        """
        Rollback Transaction
        """

        if self.connection:

            self.connection.rollback()

    def close(self):
        """
        Close Connection
        """

        if self.cursor:

            self.cursor.close()

        if self.connection:

            self.connection.close()

            self.connection = None

            self.cursor = None


db = Database()


def initialize_database():
    """
    Initialize database and run migrations.
    """
    from database.migrate import migrate
    migrate()