from pathlib import Path

from PySide6.QtCore import QObject, Signal

from services.art_copy_service import ArtCopyService


class ArtCopyWorker(QObject):

    progress = Signal(int, int)
    finished = Signal(object)

    def __init__(
            self,
            source_art: Path,
            destination_arts: list[Path],
            service: ArtCopyService,
    ):
        super().__init__()

        self.source_art = source_art
        self.destination_arts = destination_arts
        self.service = service

    def run(self):
        try:
            total = len(self.destination_arts)

            for current, destination_art in enumerate(
                    self.destination_arts,
                    start=1,
            ):
                self.service.copy_art(
                    self.source_art,
                    destination_art,
                )

                self.progress.emit(current, total)

            self.finished.emit(True)

        except Exception as e:
            self.finished.emit(e)