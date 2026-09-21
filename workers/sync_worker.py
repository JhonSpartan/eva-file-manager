from PySide6.QtCore import QObject, Signal, Slot
from database.database import Database
from database.cloud_database import CloudDatabase
from database.repositories.cloud_sync_repository import CloudSyncRepository
from services.sync_service import SyncService


class SyncWorker(QObject):

    finished = Signal(dict)
    failed = Signal(str)

    services_ready = Signal(
        object,
        object,
    )

    def __init__(
            self,
            database: Database,
            cloud_database: CloudDatabase,
            sync_service: SyncService | None,
    ) -> None:
        super().__init__()

        self.database = database
        self.cloud_database = cloud_database
        self.sync_service = sync_service

    @Slot()
    def run(self) -> None:

        try:
            if self.sync_service is None:

                self.cloud_database.initialize()

                cloud_sync_repository = CloudSyncRepository(
                    self.cloud_database
                )

                self.sync_service = SyncService(
                    self.database,
                    cloud_sync_repository,
                )

                self.services_ready.emit(
                    cloud_sync_repository,
                    self.sync_service,
                )

            result = self.sync_service.sync()

        except Exception as error:
            self.failed.emit(
                str(error)
            )
            return

        self.finished.emit(
            result
        )