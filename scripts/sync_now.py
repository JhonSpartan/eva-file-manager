from config.settings import DB_PATH

from database.cloud_database import CloudDatabase
from database.database import Database
from database.repositories.cloud_sync_repository import CloudSyncRepository
from services.sync_service import SyncService


def main() -> None:
    
    local_database = Database(
        DB_PATH
    )

    local_database.initialize()

    cloud_database = CloudDatabase()
    cloud_database.initialize()

    cloud_repository = CloudSyncRepository(
        cloud_database
    )

    sync_service = SyncService(
        local_database=local_database,
        cloud_repository=cloud_repository,
    )

    result = sync_service.sync()

    print(
        "SYNC RESULT:",
        result,
    )


if __name__ == "__main__":
    main()