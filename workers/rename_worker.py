from PySide6.QtCore import QObject, Signal, Slot
from models.results import RenameResult, RenameFileResult
from pathlib import Path
from services.file_service import FileService
from config.settings import LOG_DIR

class RenameWorker(QObject):
    progress = Signal(int, int, RenameFileResult)      # current, total
    finished = Signal(RenameResult)
    failed = Signal(str)

    def __init__(self, files: list[Path], service: FileService):
        super().__init__()
        self.files = files
        self.service = service

    @Slot()
    def run(self):
        result = RenameResult()
        total = len(self.files)
        log_path = LOG_DIR

        try:
            for index, file in enumerate(
                    self.files,
                    start=1,
            ):
                file_result = (
                    self.service.rename_one_file(
                        file,
                        result,
                    )
                )

                self.progress.emit(
                    index,
                    total,
                    file_result,
                )

            if result.errors:
                self.service.log_errors(
                    log_path,
                    result.errors,
                )

        except Exception as error:
            self.failed.emit(
                str(error)
            )
            return

        self.finished.emit(
            result
        )

