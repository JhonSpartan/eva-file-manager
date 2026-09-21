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