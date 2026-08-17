import shutil
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from models.copy_models import CopyPlan
from services.art_copy_service import ArtCopyService
from services.file_service import FileService
from models.results import RenameResult



class ArtCopyWorker(QObject):

    progress = Signal(int, int)
    finished = Signal(object)

    def __init__(
            self,
            plan: CopyPlan,
            copy_service: ArtCopyService,
            file_service: FileService,
    ):
        super().__init__()

        self.plan = plan
        self.copy_service = copy_service
        self.file_service = file_service

    @Slot()
    def run(self):

        result = RenameResult()

        try:
            total = len(self.plan.destinations)

            for current, destination_plan in enumerate(
                    self.plan.destinations,
                    start=1,
            ):

                # 1. Create missing IDs
                for id_name in destination_plan.ids_to_create:
                    id_path = (
                            destination_plan.destination_art
                            / id_name
                    )

                    id_path.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                # 2. Remove selected destination files
                for file_path in destination_plan.files_to_delete:
                    if file_path.is_file():
                        file_path.unlink()

                # 3. Copy selected source files
                copied_files = []

                for source_file in destination_plan.files_to_copy:
                    destination_id = (
                            destination_plan.destination_art
                            / source_file.parent.name
                    )

                    destination_id.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    destination_file = (
                            destination_id
                            / source_file.name
                    )

                    self.copy_service.copy_file(
                        source_file,
                        destination_file,
                    )

                    copied_files.append(
                        destination_file
                    )

                # 4. Rename copied files + update DXF layers
                for copied_file in copied_files:
                    self.file_service.rename_one_file(
                        copied_file,
                        result,
                    )

                self.progress.emit(
                    current,
                    total,
                )

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit(e)


    def copy_file(
            self,
            source_file: Path,
            destination_file: Path,
    ):
        shutil.copy2(
            source_file,
            destination_file,
        )

