import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from config import DB_PATH


def backup_database():
    source = Path(DB_PATH).resolve()
    directory = source.parent / "backups"
    directory.mkdir(exist_ok=True)
    target = directory / f"db_variant_27_{datetime.now():%Y%m%d_%H%M%S_%f}.db"
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as connection:
        with closing(sqlite3.connect(target)) as destination:
            connection.backup(destination)
    return target


if __name__ == "__main__":
    print("Резервная копия:", backup_database())

