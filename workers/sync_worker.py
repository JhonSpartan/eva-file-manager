from PySide6.QtCore import QObject, Signal, Slot

from services.sync_service import SyncService


class SyncWorker(QObject):

    finished = Signal(dict)
    failed = Signal(str)

    def __init__(
            self,
            sync_service: SyncService,
    ):
        super().__init__()

        self.sync_service = sync_service

    @Slot()
    def run(self) -> None:
        try:
            result = self.sync_service.sync()

        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit(result)