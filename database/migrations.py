import sqlite3
import uuid

from datetime import datetime, timezone


class DatabaseMigrator:

    CURRENT_VERSION = 2

    def migrate(
            self,
            connection: sqlite3.Connection,
    ) -> None:

        self.ensure_schema_version_table(
            connection
        )

        current_version = (
            self.get_current_version(
                connection
            )
        )

        if current_version < 1:
            self.migrate_to_v1(
                connection
            )

            self.set_version(
                connection,
                1,
            )

            current_version = 1

        if current_version < 2:
            self.migrate_to_v2(
                connection
            )

            self.set_version(
                connection,
                2,
            )

    def ensure_schema_version_table(
            self,
            connection: sqlite3.Connection,
    ) -> None:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            )
        """)

        row = connection.execute("""
            SELECT version
            FROM schema_version
            LIMIT 1
        """).fetchone()

        if row is None:
            connection.execute("""
                INSERT INTO schema_version (
                    version
                )
                VALUES (0)
            """)

    def get_current_version(
            self,
            connection: sqlite3.Connection,
    ) -> int:

        row = connection.execute("""
            SELECT version
            FROM schema_version
            LIMIT 1
        """).fetchone()

        return int(row["version"])

    def set_version(
            self,
            connection: sqlite3.Connection,
            version: int,
    ) -> None:

        connection.execute(
            """
            UPDATE schema_version
            SET version = ?
            """,
            (version,),
        )

    def migrate_to_v1(
            self,
            connection: sqlite3.Connection,
    ) -> None:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS copy_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                UNIQUE(mode, from_id)
            )
        """)

        connection.execute("""
            INSERT OR IGNORE INTO copy_rules (
                mode,
                from_id,
                to_id
            )
            VALUES (?, ?, ?)
        """,
            ("5D", "8", "7"),
        )

        connection.execute("""
            CREATE TABLE IF NOT EXISTS template_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER NOT NULL,
                template_name TEXT NOT NULL,
                has_stoppers INTEGER NOT NULL DEFAULT 0,
                UNIQUE(folder_id, template_name)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS stopper_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stopper_name TEXT NOT NULL UNIQUE,
                diameter REAL NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path_key TEXT NOT NULL UNIQUE,
                path_value TEXT
            )
        """)

    def migrate_to_v2(
            self,
            connection: sqlite3.Connection,
    ) -> None:

        sync_tables = (
            "copy_rules",
            "template_catalog",
            "stopper_catalog",
        )

        for table_name in sync_tables:
            self.add_sync_columns(
                connection,
                table_name,
            )

            self.fill_sync_metadata(
                connection,
                table_name,
            )

    def add_sync_columns(
            self,
            connection: sqlite3.Connection,
            table_name: str,
    ) -> None:

        columns = {
            row["name"]
            for row in connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
        }

        if "uuid" not in columns:
            connection.execute(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN uuid TEXT
                """
            )

        if "updated_at" not in columns:
            connection.execute(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN updated_at TEXT
                """
            )

        if "deleted_at" not in columns:
            connection.execute(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN deleted_at TEXT
                """
            )

    def fill_sync_metadata(
            self,
            connection: sqlite3.Connection,
            table_name: str,
    ) -> None:

        rows = connection.execute(
            f"""
            SELECT id, uuid, updated_at
            FROM {table_name}
            """
        ).fetchall()

        timestamp = (
            datetime
            .now(timezone.utc)
            .isoformat()
        )

        for row in rows:

            record_uuid = row["uuid"]

            if not record_uuid:
                record_uuid = str(
                    uuid.uuid4()
                )

            updated_at = row["updated_at"]

            if not updated_at:
                updated_at = timestamp

            connection.execute(
                f"""
                UPDATE {table_name}
                SET uuid = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    record_uuid,
                    updated_at,
                    row["id"],
                ),
            )