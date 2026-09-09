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

    def get_by_diameter(
            self,
            diameter: float,
    ) -> list[StopperRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, diameter, stopper_name
                FROM stopper_catalog
                WHERE diameter = ?
                  AND deleted_at IS NULL
                ORDER BY stopper_name
                """,
                (diameter,),
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
            diameter: float,
            stopper_name: str,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO stopper_catalog (
                    diameter,
                    stopper_name
                )
                VALUES (?, ?)
                """,
                (
                    diameter,
                    stopper_name,
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

    def update(
            self,
            record_id: int,
            diameter: float,
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