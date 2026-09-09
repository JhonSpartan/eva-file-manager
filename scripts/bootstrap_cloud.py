"""
One-time/manual bootstrap utility.

Copies shared catalog data from the local SQLite database
to the central PostgreSQL database.

Not used during normal FileForge startup.
"""

from pathlib import Path

from database.cloud_database import CloudDatabase
from database.database import Database


SYNC_TABLES = (
    "copy_rules",
    "template_catalog",
    "stopper_catalog",
)


def bootstrap_table(
        local_database: Database,
        cloud_database: CloudDatabase,
        table_name: str,
) -> None:

    with local_database.connect() as local_connection:
        rows = local_connection.execute(
            f"""
            SELECT *
            FROM {table_name}
            """
        ).fetchall()

    if not rows:
        print(
            f"{table_name}: no local rows"
        )
        return

    with cloud_database.connect() as cloud_connection:
        with cloud_connection.cursor() as cursor:

            if table_name == "copy_rules":
                for row in rows:
                    cursor.execute(
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
                            %s,
                            %s,
                            %s
                        )
                        ON CONFLICT (uuid)
                        DO UPDATE SET
                            mode = EXCLUDED.mode,
                            from_id = EXCLUDED.from_id,
                            to_id = EXCLUDED.to_id,
                            updated_at = EXCLUDED.updated_at,
                            deleted_at = EXCLUDED.deleted_at
                        """,
                        (
                            row["mode"],
                            row["from_id"],
                            row["to_id"],
                            row["uuid"],
                            row["updated_at"],
                            row["deleted_at"],
                        ),
                    )

            elif table_name == "template_catalog":
                for row in rows:
                    cursor.execute(
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
                            %s,
                            %s,
                            %s
                        )
                        ON CONFLICT (uuid)
                        DO UPDATE SET
                            folder_id = EXCLUDED.folder_id,
                            template_name = EXCLUDED.template_name,
                            has_stoppers = EXCLUDED.has_stoppers,
                            updated_at = EXCLUDED.updated_at,
                            deleted_at = EXCLUDED.deleted_at
                        """,
                        (
                            row["folder_id"],
                            row["template_name"],
                            row["has_stoppers"],
                            row["uuid"],
                            row["updated_at"],
                            row["deleted_at"],
                        ),
                    )

            elif table_name == "stopper_catalog":
                for row in rows:
                    cursor.execute(
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
                            %s,
                            %s,
                            %s
                        )
                        ON CONFLICT (uuid)
                        DO UPDATE SET
                            stopper_name = EXCLUDED.stopper_name,
                            diameter = EXCLUDED.diameter,
                            updated_at = EXCLUDED.updated_at,
                            deleted_at = EXCLUDED.deleted_at
                        """,
                        (
                            row["stopper_name"],
                            row["diameter"],
                            row["uuid"],
                            row["updated_at"],
                            row["deleted_at"],
                        ),
                    )

    print(
        f"{table_name}: uploaded {len(rows)} rows"
    )

def preflight_check(
        local_database: Database,
        cloud_database: CloudDatabase,
) -> None:

    print("Bootstrap preflight:")
    print()

    for table_name in SYNC_TABLES:

        with local_database.connect() as local_connection:
            local_count = local_connection.execute(
                f"""
                SELECT COUNT(*)
                FROM {table_name}
                """
            ).fetchone()[0]

        with cloud_database.connect() as cloud_connection:
            with cloud_connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table_name}
                    """
                )

                cloud_count = cursor.fetchone()[0]

        print(
            f"{table_name}: "
            f"local={local_count}, "
            f"cloud={cloud_count}"
        )

def main() -> None:

    local_db_path = (
        Path.home()
        / ".eva"
        / "eva.db"
    )

    local_database = Database(
        local_db_path
    )

    cloud_database = CloudDatabase()

    local_database.initialize()
    cloud_database.initialize()

    preflight_check(
        local_database,
        cloud_database,
    )

    for table_name in SYNC_TABLES:
        bootstrap_table(
            local_database,
            cloud_database,
            table_name,
        )

    print(
        "Cloud bootstrap completed"
    )

if __name__ == "__main__":
    main()