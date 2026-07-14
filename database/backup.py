"""
===========================================================
CyberMind AI
Database Backup
===========================================================
"""

import shutil
from datetime import datetime

from config.settings import DATABASE_PATH
from config.settings import BASE_DIR


BACKUP_DIR = BASE_DIR / "database" / "backups"

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def create_backup():
    """
    Create Database Backup
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        BACKUP_DIR /
        f"cybermind_backup_{timestamp}.db"
    )

    shutil.copy2(
        DATABASE_PATH,
        backup_file
    )

    print(
        f"Backup Created:\n{backup_file}"
    )

    return backup_file


if __name__ == "__main__":

    create_backup()