"""
CyberMind AI
Database Connection
"""

from __future__ import annotations

from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_PATH


class DatabaseConnection:
    def __init__(self) -> None:
        self.database_url = f"sqlite:///{DATABASE_PATH.resolve()}"
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self) -> Any:
        return self.SessionLocal()

    def is_connected(self) -> bool:
        try:
            with self.engine.connect() as conn:
                return True
        except Exception:
            return False

    def health_check(self) -> dict[str, Any]:
        return {
            "status": "Healthy" if self.is_connected() else "Unhealthy"
        }

    def __repr__(self) -> str:
        return f"DatabaseConnection({self.database_url})"


database = DatabaseConnection()
