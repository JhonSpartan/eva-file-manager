from database.database import Database
from models.copy_models import CopyRule


class CopyRuleRepository:

    def __init__(
            self,
            database: Database,
    ):
        self.database = database

    def get_all(self) -> list[CopyRule]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, mode, from_id, to_id
                FROM copy_rules
                WHERE deleted_at IS NULL
                ORDER BY mode, from_id
                """
            ).fetchall()

        return [
            CopyRule(
                id=row["id"],
                mode=row["mode"],
                from_id=row["from_id"],
                to_id=row["to_id"],
            )
            for row in rows
        ]

    def get_by_id(
            self,
            record_id: int,
    ) -> CopyRule | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, mode, from_id, to_id
                FROM copy_rules
                WHERE id = ?
                  AND deleted_at IS NULL
                """,
                (record_id,),
            ).fetchone()

        if row is None:
            return None

        return CopyRule(
            id=row["id"],
            mode=row["mode"],
            from_id=row["from_id"],
            to_id=row["to_id"],
        )

    def get_destination_id(
            self,
            mode: str,
            source_id: str,
    ) -> str | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT to_id
                FROM copy_rules
                WHERE mode = ?
                  AND from_id = ?
                  AND deleted_at IS NULL
                LIMIT 1
                """,
                (
                    mode,
                    source_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return row["to_id"]

    def get_uuid_by_id(
            self,
            record_id: int,
    ) -> str | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT uuid
                FROM copy_rules
                WHERE id = ?
                  AND deleted_at IS NULL
                """,
                (
                    record_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return row["uuid"]