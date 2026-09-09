from database.cloud_database import CloudDatabase
from database.repositories.cloud_sync_repository import CloudSyncRepository


def main() -> None:

    cloud_database = CloudDatabase()

    repository = CloudSyncRepository(
        cloud_database
    )

    rules = repository.get_copy_rules()

    print(
        "Cloud copy rules:",
        len(rules),
    )

    for rule in rules:
        print(
            rule["mode"],
            rule["from_id"],
            "->",
            rule["to_id"],
        )


if __name__ == "__main__":
    main()