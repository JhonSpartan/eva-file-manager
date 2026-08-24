from models.copy_models import CopyRule
from database.database import Database


class CopyRuleRepository:

    def __init__(self, database: Database):
        self.database = database

    def get_rules(self, mode: str) -> list[CopyRule]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT mode, from_id, to_id
                FROM copy_rules
                WHERE mode = ?
                """,
                (mode,),
            ).fetchall()

        return [
            CopyRule(
                mode=row["mode"],
                from_id=row["from_id"],
                to_id=row["to_id"],
            )
            for row in rows
        ]

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
                WHERE mode = ? AND from_id = ?
                LIMIT 1
                """,
                (mode, source_id),
            ).fetchone()

        if row is None:
            return None

        return row["to_id"]