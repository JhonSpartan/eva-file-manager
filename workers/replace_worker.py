from PySide6.QtCore import QObject, Signal, Slot
from models.results import ReplaceResult, RenameFileResult
from pathlib import Path
from services.file_service import FileService

class ReplaceWorker(QObject):
    progress = Signal(int, int, RenameFileResult)      # current, total
    finished = Signal(ReplaceResult)        # итоговый результат

    def __init__(self, files: list[Path], find_text: str, replace_text: str, service: FileService):
        super().__init__()
        self.files = files
        self.service = service
        self.find_text = find_text
        self.replace_text = replace_text


    @Slot()
    def run(self):
        result = ReplaceResult()
        total = len(self.files)

        for index, file in enumerate(self.files, start=1):
            file_result = self.service.replace_chars_in_one_file(file, self.find_text, self.replace_text, result)
            self.progress.emit(index, total, file_result)

        self.finished.emit(result)
