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

    def add(
            self,
            mode: str,
            from_id: str,
            to_id: str,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO copy_rules (
                    mode,
                    from_id,
                    to_id
                )
                VALUES (?, ?, ?)
                """,
                (mode, from_id, to_id),
            )

    def update(
            self,
            record_id: int,
            mode: str,
            from_id: str,
            to_id: str,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE copy_rules
                SET mode = ?,
                    from_id = ?,
                    to_id = ?
                WHERE id = ?
                """,
                (
                    mode,
                    from_id,
                    to_id,
                    record_id,
                ),
            )

    def delete_by_ids(
            self,
            record_ids: list[int],
    ):
        if not record_ids:
            return

        placeholders = ",".join(
            "?"
            for _ in record_ids
        )

        with self.database.connect() as connection:
            connection.execute(
                f"""
                DELETE FROM copy_rules
                WHERE id IN ({placeholders})
                """,
                record_ids,
            )