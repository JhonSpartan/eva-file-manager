import sqlite3
from pathlib import Path

from database.migrations import DatabaseMigrator


class Database:

    def __init__(
            self,
            db_path: Path,
    ):
        self.db_path = db_path

    def connect(
            self,
    ) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.db_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def initialize(
            self,
    ) -> None:

        with self.connect() as connection:

            migrator = DatabaseMigrator()

            migrator.migrate(
                connection
            )