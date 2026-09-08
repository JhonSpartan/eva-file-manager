from pathlib import Path

from database.database import Database
from models.path_models import PathRecord


class PathRepository:
    def __init__(
            self,
            database: Database,
    ):
        self.database = database

    def get_by_key(
            self,
            key: str,
    ) -> PathRecord | None:

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    path_key,
                    path_value
                FROM paths
                WHERE path_key = ?
                LIMIT 1
                """,
                (key,),
            ).fetchone()

        if row is None:
            return None

        path_value = row["path_value"]

        return PathRecord(
            id=row["id"],
            key=row["path_key"],
            path=(
                Path(path_value)
                if path_value
                else None
            ),
        )

    def save(
            self,
            key: str,
            path: Path | None,
    ) -> None:

        path_value = (
            str(path)
            if path is not None
            else None
        )

        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO paths (
                    path_key,
                    path_value
                )
                VALUES (?, ?)

                ON CONFLICT(path_key)
                DO UPDATE SET
                    path_value = excluded.path_value
                """,
                (
                    key,
                    path_value,
                ),
            )