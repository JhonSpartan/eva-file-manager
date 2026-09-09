from database.database import Database
from database.repositories.cloud_sync_repository import CloudSyncRepository



class SyncService:

    def __init__(
            self,
            local_database: Database,
            cloud_repository: CloudSyncRepository,
    ):
        self.local_database = local_database
        self.cloud_repository = cloud_repository

    def sync_copy_rules(
            self,
    ) -> int:

        cloud_rules = (
            self.cloud_repository
            .get_copy_rules()
        )

        synced_count = 0

        with self.local_database.connect() as connection:

            for rule in cloud_rules:

                cloud_uuid = str(
                    rule["uuid"]
                )

                # Сначала ищем по глобальному UUID.
                existing_row = connection.execute(
                    """
                    SELECT id
                    FROM copy_rules
                    WHERE uuid = ?
                    """,
                    (
                        cloud_uuid,
                    ),
                ).fetchone()

                # Если UUID отличается, возможно это старая
                # локальная запись, созданная до первой sync.
                if existing_row is None:
                    existing_row = connection.execute(
                        """
                        SELECT id
                        FROM copy_rules
                        WHERE mode = ?
                          AND from_id = ?
                        """,
                        (
                            rule["mode"],
                            rule["from_id"],
                        ),
                    ).fetchone()

                # Если запись удалена в cloud,
                # локально тоже ставим tombstone.
                if rule["deleted_at"] is not None:

                    if existing_row is not None:
                        connection.execute(
                            """
                            UPDATE copy_rules
                            SET uuid = ?,
                                updated_at = ?,
                                deleted_at = ?
                            WHERE id = ?
                            """,
                            (
                                cloud_uuid,
                                rule["updated_at"].isoformat(),
                                rule["deleted_at"].isoformat(),
                                existing_row["id"],
                            ),
                        )

                    synced_count += 1
                    continue

                # Активная cloud-запись.
                if existing_row is None:
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
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            rule["mode"],
                            rule["from_id"],
                            rule["to_id"],
                            cloud_uuid,
                            rule["updated_at"].isoformat(),
                            None,
                        ),
                    )

                else:
                    connection.execute(
                        """
                        UPDATE copy_rules
                        SET mode = ?,
                            from_id = ?,
                            to_id = ?,
                            uuid = ?,
                            updated_at = ?,
                            deleted_at = ?
                        WHERE id = ?
                        """,
                        (
                            rule["mode"],
                            rule["from_id"],
                            rule["to_id"],
                            cloud_uuid,
                            rule["updated_at"].isoformat(),
                            None,
                            existing_row["id"],
                        ),
                    )

                synced_count += 1

        return synced_count

    def sync_templates(
            self,
    ) -> int:

        cloud_templates = (
            self.cloud_repository
            .get_templates()
        )

        synced_count = 0

        with self.local_database.connect() as connection:

            for template in cloud_templates:

                cloud_uuid = str(
                    template["uuid"]
                )

                existing_row = connection.execute(
                    """
                    SELECT id
                    FROM template_catalog
                    WHERE uuid = ?
                    """,
                    (
                        cloud_uuid,
                    ),
                ).fetchone()

                if existing_row is None:
                    existing_row = connection.execute(
                        """
                        SELECT id
                        FROM template_catalog
                        WHERE folder_id = ?
                          AND template_name = ?
                        """,
                        (
                            template["folder_id"],
                            template["template_name"],
                        ),
                    ).fetchone()

                if template["deleted_at"] is not None:

                    if existing_row is not None:
                        connection.execute(
                            """
                            UPDATE template_catalog
                            SET uuid = ?,
                                updated_at = ?,
                                deleted_at = ?
                            WHERE id = ?
                            """,
                            (
                                cloud_uuid,
                                template["updated_at"].isoformat(),
                                template["deleted_at"].isoformat(),
                                existing_row["id"],
                            ),
                        )

                    synced_count += 1
                    continue

                if existing_row is None:
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
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            template["folder_id"],
                            template["template_name"],
                            template["has_stoppers"],
                            cloud_uuid,
                            template["updated_at"].isoformat(),
                            None,
                        ),
                    )

                else:
                    connection.execute(
                        """
                        UPDATE template_catalog
                        SET folder_id = ?,
                            template_name = ?,
                            has_stoppers = ?,
                            uuid = ?,
                            updated_at = ?,
                            deleted_at = ?
                        WHERE id = ?
                        """,
                        (
                            template["folder_id"],
                            template["template_name"],
                            template["has_stoppers"],
                            cloud_uuid,
                            template["updated_at"].isoformat(),
                            None,
                            existing_row["id"],
                        ),
                    )

                synced_count += 1

        return synced_count

    def sync_stoppers(
            self,
    ) -> int:

        cloud_stoppers = (
            self.cloud_repository
            .get_stoppers()
        )

        synced_count = 0

        with self.local_database.connect() as connection:

            for stopper in cloud_stoppers:

                cloud_uuid = str(
                    stopper["uuid"]
                )

                existing_row = connection.execute(
                    """
                    SELECT id
                    FROM stopper_catalog
                    WHERE uuid = ?
                    """,
                    (
                        cloud_uuid,
                    ),
                ).fetchone()

                if existing_row is None:
                    existing_row = connection.execute(
                        """
                        SELECT id
                        FROM stopper_catalog
                        WHERE stopper_name = ?
                        """,
                        (
                            stopper["stopper_name"],
                        ),
                    ).fetchone()

                if stopper["deleted_at"] is not None:

                    if existing_row is not None:
                        connection.execute(
                            """
                            UPDATE stopper_catalog
                            SET uuid = ?,
                                updated_at = ?,
                                deleted_at = ?
                            WHERE id = ?
                            """,
                            (
                                cloud_uuid,
                                stopper["updated_at"].isoformat(),
                                stopper["deleted_at"].isoformat(),
                                existing_row["id"],
                            ),
                        )

                    synced_count += 1
                    continue

                if existing_row is None:
                    connection.execute(
                        """
                        INSERT INTO stopper_catalog (
                            stopper_name,
                            diameter,
                            uuid,
                            updated_at,
                            deleted_at
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            stopper["stopper_name"],
                            stopper["diameter"],
                            cloud_uuid,
                            stopper["updated_at"].isoformat(),
                            None,
                        ),
                    )

                else:
                    connection.execute(
                        """
                        UPDATE stopper_catalog
                        SET stopper_name = ?,
                            diameter = ?,
                            uuid = ?,
                            updated_at = ?,
                            deleted_at = ?
                        WHERE id = ?
                        """,
                        (
                            stopper["stopper_name"],
                            stopper["diameter"],
                            cloud_uuid,
                            stopper["updated_at"].isoformat(),
                            None,
                            existing_row["id"],
                        ),
                    )

                synced_count += 1

        return synced_count

    def sync(self) -> dict[str, int]:

        return {
            "copy_rules": self.sync_copy_rules(),
            "template_catalog": self.sync_templates(),
            "stopper_catalog": self.sync_stoppers(),
        }

