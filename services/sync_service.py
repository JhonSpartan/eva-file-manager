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

                if rule["deleted_at"] is not None:
                    continue

                existing_row = connection.execute(
                    """
                    SELECT id
                    FROM copy_rules
                    WHERE uuid = ?
                    """,
                    (
                        str(rule["uuid"]),
                    ),
                ).fetchone()

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
                            str(rule["uuid"]),
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
                            updated_at = ?,
                            deleted_at = ?
                        WHERE uuid = ?
                        """,
                        (
                            rule["mode"],
                            rule["from_id"],
                            rule["to_id"],
                            rule["updated_at"].isoformat(),
                            None,
                            str(rule["uuid"]),
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

                if template["deleted_at"] is not None:
                    continue

                existing_row = connection.execute(
                    """
                    SELECT id
                    FROM template_catalog
                    WHERE uuid = ?
                    """,
                    (
                        str(template["uuid"]),
                    ),
                ).fetchone()

                values = (
                    template["folder_id"],
                    template["template_name"],
                    template["has_stoppers"],
                    template["updated_at"].isoformat(),
                )

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
                            str(template["uuid"]),
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
                            updated_at = ?,
                            deleted_at = ?
                        WHERE uuid = ?
                        """,
                        (
                            *values,
                            None,
                            str(template["uuid"]),
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

                if stopper["deleted_at"] is not None:
                    continue

                existing_row = connection.execute(
                    """
                    SELECT id
                    FROM stopper_catalog
                    WHERE uuid = ?
                    """,
                    (
                        str(stopper["uuid"]),
                    ),
                ).fetchone()

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
                            str(stopper["uuid"]),
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
                            updated_at = ?,
                            deleted_at = ?
                        WHERE uuid = ?
                        """,
                        (
                            stopper["stopper_name"],
                            stopper["diameter"],
                            stopper["updated_at"].isoformat(),
                            None,
                            str(stopper["uuid"]),
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