from database.cloud_database import CloudDatabase


class CloudSyncRepository:

    def __init__(
            self,
            database: CloudDatabase,
    ):
        self.database = database

    def get_copy_rules(
            self,
    ) -> list[dict]:

        with self.database.connect() as connection:
            with connection.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        mode,
                        from_id,
                        to_id,
                        uuid,
                        updated_at,
                        deleted_at
                    FROM copy_rules
                """)

                columns = [
                    description.name
                    for description
                    in cursor.description
                ]

                return [
                    dict(
                        zip(
                            columns,
                            row,
                        )
                    )
                    for row in cursor.fetchall()
                ]

    def get_templates(
            self,
    ) -> list[dict]:
        with self.database.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        folder_id,
                        template_name,
                        has_stoppers,
                        uuid,
                        updated_at,
                        deleted_at
                    FROM template_catalog
                """)

                columns = [
                    description.name
                    for description
                    in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

    def get_stoppers(
            self,
    ) -> list[dict]:
        with self.database.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        stopper_name,
                        diameter,
                        uuid,
                        updated_at,
                        deleted_at
                    FROM stopper_catalog
                """)

                columns = [
                    description.name
                    for description
                    in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]