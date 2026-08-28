import sqlite3
from pathlib import Path


class Database:

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        return connection

    def initialize(self):
        with self.connect() as connection:
            # Copy rules
            connection.execute("""
                CREATE TABLE IF NOT EXISTS copy_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    from_id TEXT NOT NULL,
                    to_id TEXT NOT NULL,
                    UNIQUE(mode, from_id)
                )
            """)

            # Initial 5D rule
            connection.execute(
                """
                INSERT OR IGNORE INTO copy_rules (
                    mode,
                    from_id,
                    to_id
                )
                VALUES (?, ?, ?)
                """,
                ("5D", "8", "7"),
            )

            # Template catalog
            connection.execute("""
                CREATE TABLE IF NOT EXISTS template_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder_id INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    has_stoppers INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(folder_id, template_name)
                )
            """)

            # Stopper catalog
            connection.execute("""
                CREATE TABLE IF NOT EXISTS stopper_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stopper_name TEXT NOT NULL UNIQUE,
                    diameter REAL NOT NULL
                )
            """)