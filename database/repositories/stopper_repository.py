from database.database import Database
from models.catalog_models import StopperRecord


class StopperRepository:

    def __init__(
            self,
            database: Database,
    ):
        self.database = database

    def get_all(self) -> list[StopperRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, diameter, stopper_name
                FROM stopper_catalog
                ORDER BY diameter, stopper_name
                """
            ).fetchall()

        return [
            StopperRecord(
                id=row["id"],
                diameter=row["diameter"],
                stopper_name=row["stopper_name"],
            )
            for row in rows
        ]

    def get_by_folder_id(
            self,
            folder_id: int,
    ) -> list[StopperRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, diameter, stopper_name
                FROM stopper_catalog
                WHERE diameter = ?
                ORDER BY stopper_name
                """,
                (folder_id,),
            ).fetchall()

        return [
            StopperRecord(
                id=row["id"],
                diameter=row["diameter"],
                stopper_name=row["stopper_name"],
            )
            for row in rows
        ]

    def add(
            self,
            diameter: int,
            stopper_name: str,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO stopper_catalog (
                    diameter,
                    stopper_name
                )
                VALUES (?, ?)
                """,
                (diameter, stopper_name),
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
                DELETE FROM stopper_catalog
                WHERE id IN ({placeholders})
                """,
                record_ids,
            )

    def get_by_id(
            self,
            record_id: int,
    ) -> StopperRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, diameter, stopper_name
                FROM stopper_catalog
                WHERE id = ?
                """,
                (record_id,),
            ).fetchone()

        if row is None:
            return None

        return StopperRecord(
            id=row["id"],
            diameter=row["diameter"],
            stopper_name=row["stopper_name"],
        )

    def update(
            self,
            record_id: int,
            diameter: int,
            stopper_name: str,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE stopper_catalog
                SET diameter = ?,
                    stopper_name = ?
                WHERE id = ?
                """,
                (
                    diameter,
                    stopper_name,
                    record_id,
                ),
            )