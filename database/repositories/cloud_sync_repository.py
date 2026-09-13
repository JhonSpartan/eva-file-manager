from database.cloud_database import CloudDatabase


class CloudSyncRepository:

    def __init__(
            self,
            database: CloudDatabase,
    ) -> None:
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
                    dict(zip(columns, row))
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

    def add_template(
            self,
            folder_id: int,
            template_name: str,
            has_stoppers: bool,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO template_catalog (
                    folder_id,
                    template_name,
                    has_stoppers,
                    uuid,
                    updated_at,
                    deleted_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    gen_random_uuid(),
                    NOW(),
                    NULL
                )
                """,
                (
                    folder_id,
                    template_name,
                    int(has_stoppers),
                ),
            )

    def update_template(
            self,
            template_uuid: str,
            folder_id: int,
            template_name: str,
            has_stoppers: bool,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE template_catalog
                SET
                    folder_id = %s,
                    template_name = %s,
                    has_stoppers = %s,
                    updated_at = NOW()
                WHERE uuid = %s
                  AND deleted_at IS NULL
                """,
                (
                    folder_id,
                    template_name,
                    int(has_stoppers),
                    template_uuid,
                ),
            )

    def delete_template(
            self,
            template_uuid: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE template_catalog
                SET
                    deleted_at = NOW(),
                    updated_at = NOW()
                WHERE uuid = %s
                  AND deleted_at IS NULL
                """,
                (
                    template_uuid,
                ),
            )

    def add_stopper(
            self,
            stopper_name: str,
            diameter: float,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO stopper_catalog (
                    stopper_name,
                    diameter,
                    uuid,
                    updated_at,
                    deleted_at
                )
                VALUES (
                    %s,
                    %s,
                    gen_random_uuid(),
                    NOW(),
                    NULL
                )
                """,
                (
                    stopper_name,
                    diameter,
                ),
            )

    def update_stopper(
            self,
            stopper_uuid: str,
            stopper_name: str,
            diameter: float,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE stopper_catalog
                SET
                    stopper_name = %s,
                    diameter = %s,
                    updated_at = NOW()
                WHERE uuid = %s
                  AND deleted_at IS NULL
                """,
                (
                    stopper_name,
                    diameter,
                    stopper_uuid,
                ),
            )

    def delete_stopper(
            self,
            stopper_uuid: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE stopper_catalog
                SET
                    deleted_at = NOW(),
                    updated_at = NOW()
                WHERE uuid = %s
                  AND deleted_at IS NULL
                """,
                (
                    stopper_uuid,
                ),
            )

    def add_copy_rule(
            self,
            mode: str,
            from_id: str,
            to_id: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO copy_rules (
                    mode,
                    from_id,
                    to_id,
                    uuid,
                    updated_at,
                    deleted_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    gen_random_uuid(),
                    NOW(),
                    NULL
                )
                """,
                (
                    mode,
                    from_id,
                    to_id,
                ),
            )

    def update_copy_rule(
            self,
            rule_uuid: str,
            mode: str,
            from_id: str,
            to_id: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE copy_rules
                SET
                    mode = %s,
                    from_id = %s,
                    to_id = %s,
                    updated_at = NOW()
                WHERE uuid = %s
                  AND deleted_at IS NULL
                """,
                (
                    mode,
                    from_id,
                    to_id,
                    rule_uuid,
                ),
            )

    def delete_copy_rule(
            self,
            rule_uuid: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE copy_rules
                SET
                    deleted_at = NOW(),
                    updated_at = NOW()
                WHERE uuid = %s
                  AND deleted_at IS NULL
                """,
                (
                    rule_uuid,
                ),
            )