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
                WHERE deleted_at IS NULL
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
                  AND deleted_at IS NULL
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

    def get_uuid_by_id(
            self,
            record_id: int,
    ) -> str | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT uuid
                FROM stopper_catalog
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

    def get_by_name(
            self,
            stopper_name: str,
    ) -> StopperRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, diameter, stopper_name
                FROM stopper_catalog
                WHERE stopper_name = ?
                  AND deleted_at IS NULL
                """,
                (
                    stopper_name,
                ),
            ).fetchone()

        if row is None:
            return None

        return StopperRecord(
            id=row["id"],
            diameter=row["diameter"],
            stopper_name=row["stopper_name"],
        )