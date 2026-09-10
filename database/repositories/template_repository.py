from database.database import Database
from models.catalog_models import TemplateRecord


class TemplateRepository:

    def __init__(
            self,
            database: Database,
    ):
        self.database = database

    def get_all(self) -> list[TemplateRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, folder_id, template_name, has_stoppers
                FROM template_catalog
                WHERE deleted_at IS NULL
                ORDER BY folder_id, template_name
                """
            ).fetchall()

        return [
            TemplateRecord(
                id=row["id"],
                folder_id=row["folder_id"],
                template_name=row["template_name"],
                has_stoppers=bool(row["has_stoppers"]),
            )
            for row in rows
        ]

    def get_by_folder_id(
            self,
            folder_id: int,
    ) -> list[TemplateRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, folder_id, template_name, has_stoppers
                FROM template_catalog
                WHERE folder_id = ?
                  AND deleted_at IS NULL
                ORDER BY template_name
                """,
                (folder_id,),
            ).fetchall()

        return [
            TemplateRecord(
                id=row["id"],
                folder_id=row["folder_id"],
                template_name=row["template_name"],
                has_stoppers=bool(row["has_stoppers"]),
            )
            for row in rows
        ]

    def add(
            self,
            folder_id: int,
            template_name: str,
            has_stoppers: bool,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO template_catalog (
                    folder_id,
                    template_name,
                    has_stoppers
                )
                VALUES (?, ?, ?)
                """,
                (
                    folder_id,
                    template_name,
                    int(has_stoppers),
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
                DELETE FROM template_catalog
                WHERE id IN ({placeholders})
                """,
                record_ids,
            )

    def get_by_id(
            self,
            record_id: int,
    ) -> TemplateRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, folder_id, template_name, has_stoppers
                FROM template_catalog
                WHERE id = ?
                  AND deleted_at IS NULL
                """,
                (record_id,),
            ).fetchone()

        if row is None:
            return None

        return TemplateRecord(
            id=row["id"],
            folder_id=row["folder_id"],
            template_name=row["template_name"],
            has_stoppers=bool(row["has_stoppers"]),
        )

    def update(
            self,
            record_id: int,
            folder_id: int,
            template_name: str,
            has_stoppers: bool,
    ):
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE template_catalog
                SET
                    folder_id = ?,
                    template_name = ?,
                    has_stoppers = ?
                WHERE id = ?
                """,
                (
                    folder_id,
                    template_name,
                    int(has_stoppers),
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
                FROM template_catalog
                WHERE id = ?
                  AND deleted_at IS NULL
                """,
                (record_id,),
            ).fetchone()

            if row is None:
                return None

            return row["uuid"]

    def get_by_name(
            self,
            template_name: str,
    ) -> TemplateRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, folder_id, template_name, has_stoppers
                FROM template_catalog
                WHERE template_name = ?
                  AND deleted_at IS NULL
                """,
                (
                    template_name,
                ),
            ).fetchone()

        if row is None:
            return None

        return TemplateRecord(
            id=row["id"],
            folder_id=row["folder_id"],
            template_name=row["template_name"],
            has_stoppers=bool(row["has_stoppers"]),
        )