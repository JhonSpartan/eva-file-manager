from pathlib import Path

from database.cloud_database import CloudDatabase
from database.database import Database
from database.repositories.cloud_sync_repository import CloudSyncRepository
from services.sync_service import SyncService
from database.repositories.copy_rule_repository import CopyRuleRepository
from database.repositories.template_repository import TemplateRepository
from database.repositories.stopper_repository import StopperRepository

def print_local_copy_rule(
        local_database: Database,
        label: str,
) -> None:

    with local_database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                mode,
                from_id,
                to_id,
                uuid,
                updated_at,
                deleted_at
            FROM copy_rules
            WHERE mode = ?
              AND from_id = ?
            """,
            (
                "5D",
                "8",
            ),
        ).fetchone()

    print()
    print(label)

    if row is None:
        print("copy_rule not found")
        return

    print(dict(row))

def print_local_template(
        local_database: Database,
        label: str,
) -> None:

    with local_database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                folder_id,
                template_name,
                has_stoppers,
                uuid,
                updated_at,
                deleted_at
            FROM template_catalog
            WHERE folder_id = ?
              AND template_name = ?
            """,
            (
                8,
                "tunnel",
            ),
        ).fetchone()

    print()
    print(label)

    if row is None:
        print("template not found")
        return

    print(dict(row))

def print_local_stopper(
        local_database: Database,
        label: str,
) -> None:

    with local_database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                stopper_name,
                diameter,
                uuid,
                updated_at,
                deleted_at
            FROM stopper_catalog
            WHERE stopper_name = ?
            """,
            (
                "AV",
            ),
        ).fetchone()

    print()
    print(label)

    if row is None:
        print("stopper not found")
        return

    print(dict(row))


def main() -> None:

    local_db_path = (
        Path.home()
        / ".eva"
        / "eva.db"
    )

    local_database = Database(
        local_db_path
    )

    copy_rule_repository = CopyRuleRepository(
        local_database
    )
    template_repository = TemplateRepository(
        local_database
    )
    stopper_repository = StopperRepository(
        local_database
    )

    local_database.initialize()

    cloud_database = CloudDatabase()

    cloud_database.initialize()

    cloud_repository = CloudSyncRepository(
        cloud_database
    )

    cloud_repository = CloudSyncRepository(
        cloud_database
    )
    cloud_repository.delete_copy_rule(
        rule_uuid="75d915da-c96d-4302-8ce6-a575403d2630",
    )
    print()
    print("CLOUD COPY RULE AFTER DELETE:")

    for rule in cloud_repository.get_copy_rules():
        if str(rule["uuid"]) == (
                "75d915da-c96d-4302-8ce6-a575403d2630"
        ):
            print(rule)


    for template in cloud_repository.get_templates():
        if str(template["uuid"]) == (
                "fb0841a2-2dcc-4cdf-ad6e-0596d11d760d"
        ):
            print(template)

    cloud_templates = (
        cloud_repository
        .get_templates()
    )

    print()
    print("CLOUD TEMPLATES AFTER ADD:")

    for template in cloud_templates:
        if (
                template["folder_id"] == 99
                and template["template_name"] == "sync_test_template"
        ):
            print(template)

    sync_service = SyncService(
        local_database=local_database,
        cloud_repository=cloud_repository,
    )

    # 1. Смотрим локальную запись ДО sync
    print_local_copy_rule(
        local_database,
        "LOCAL BEFORE SYNC:",
    )

    # 2. Смотрим, что реально пришло из Neon
    cloud_rules = (
        cloud_repository
        .get_copy_rules()
    )

    print()
    print("CLOUD DATA:")

    for rule in cloud_rules:
        print(rule)

    print_local_template(
        local_database,
        "TEMPLATE BEFORE SYNC:",
    )

    print_local_stopper(
        local_database,
        "STOPPER BEFORE SYNC:",
    )

    # 3. Запускаем синхронизацию
    result = sync_service.sync()

    with local_database.connect() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                mode,
                from_id,
                to_id,
                uuid,
                updated_at,
                deleted_at
            FROM copy_rules
            WHERE uuid = ?
            """,
            (
                "75d915da-c96d-4302-8ce6-a575403d2630",
            ),
        ).fetchall()

    print()
    print("LOCAL TEST COPY RULE AFTER UPDATE SYNC:")

    for row in rows:
        print(dict(row))

    print("MATCHING ROW COUNT:", len(rows))

    print(
        "SYNC RESULT:",
        result,
    )

    print_local_template(
        local_database,
        "TEMPLATE AFTER SYNC:",
    )

    print_local_stopper(
        local_database,
        "STOPPER AFTER SYNC:",
    )
    templates = (
        template_repository
        .get_by_folder_id(8)
    )

    stoppers = (
        stopper_repository
        .get_by_diameter(26)
    )

    print()
    print(
        "TEMPLATES FROM REPOSITORY:",
        [
            template.template_name
            for template in templates
        ],
    )

    print(
        "STOPPERS FROM REPOSITORY:",
        [
            stopper.stopper_name
            for stopper in stoppers
        ],
    )

    # 4. Смотрим локальную запись ПОСЛЕ sync
    print_local_copy_rule(
        local_database,
        "LOCAL AFTER SYNC:",
    )

    destination_id = (
        copy_rule_repository
        .get_destination_id(
            "5D",
            "8",
        )
    )

    print()
    print(
        "REPOSITORY DESTINATION:",
        destination_id,
    )

    with local_database.connect() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                stopper_name,
                diameter,
                uuid,
                updated_at,
                deleted_at
            FROM stopper_catalog
            WHERE stopper_name = ?
            """,
            (
                "SYNC_TEST_STOPPER",
            ),
        ).fetchall()

    print()
    print("LOCAL TEST STOPPER AFTER SYNC:")

    for row in rows:
        print(dict(row))

    print("MATCHING ROW COUNT:", len(rows))




if __name__ == "__main__":
    main()