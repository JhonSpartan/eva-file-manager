from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from services.art_copy_service import ArtCopyService
from services.file_service import FileService
from models.results import RenameResult



class ArtCopyWorker(QObject):

    progress = Signal(int, int)
    finished = Signal(object)

    def __init__(
            self,
            source_art: Path,
            destination_arts: list[Path],
            copy_service: ArtCopyService,
            file_service: FileService,
    ):
        super().__init__()

        self.source_art = source_art
        self.destination_arts = destination_arts
        self.copy_service =  copy_service
        self.file_service = file_service

    @Slot()
    def run(self):

        result = RenameResult()

        try:
            total = len(self.destination_arts)

            for current, destination_art in enumerate(
                    self.destination_arts,
                    start=1,
            ):

                # 1. Очистка destination
                self.copy_service.clear_art(
                    destination_art
                )

                # 2. Копирование
                self.copy_service.copy_art(
                    self.source_art,
                    destination_art,
                )

                # 3. Получаем DXF
                files = self.file_service.get_dxf_files(
                    destination_art
                )

                # 4. Rename + layers
                for file in files:
                    self.file_service.rename_one_file(
                        file,
                        result,
                    )

                self.progress.emit(
                    current,
                    total,
                )

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit(e)