import psycopg

from config.settings import FILEFORGE_DATABASE_URL
from database.cloud_migrations import CloudDatabaseMigrator


class CloudDatabase:

    def connect(self):
        if not FILEFORGE_DATABASE_URL:
            raise RuntimeError(
                "FILEFORGE_DATABASE_URL is not configured"
            )

        return psycopg.connect(
            FILEFORGE_DATABASE_URL
        )

    def initialize(self) -> None:
        with self.connect() as connection:
            migrator = CloudDatabaseMigrator()

            migrator.migrate(
                connection
            )