import shutil
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from models.copy_models import CopyPlan
from services.art_copy_service import ArtCopyService
from services.file_service import FileService
from models.results import CopyArtResult


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

    def _count_operations(self) -> int:
        total = 0

        for destination_plan in self.plan.destinations:
            create_count = len(destination_plan.ids_to_create)
            delete_count = len(destination_plan.files_to_delete)
            copy_count = len(destination_plan.copy_operations)
            rename_count = copy_count

            total += (
                    create_count
                    + delete_count
                    + copy_count
                    + rename_count
            )

        return total

    @Slot()
    def run(self):

        result = CopyArtResult()

        try:
            total = self._count_operations()
            current = 0

            for destination_plan in self.plan.destinations:

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
                    result.created_ids += 1

                    current += 1
                    self.progress.emit(current, total)

                # 2. Remove selected destination files
                for file_path in destination_plan.files_to_delete:
                    if file_path.is_file():
                        file_path.unlink()
                        result.deleted_files += 1

                    current += 1
                    self.progress.emit(current, total)

                # 3. Copy selected source files
                copied_files = []

                for operation in destination_plan.copy_operations:
                    source_file = operation.source_file
                    destination_id = operation.destination_id

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

                    result.copied_files += 1

                    copied_files.append(
                        destination_file
                    )

                    current += 1
                    self.progress.emit(current, total)

                # 4. Rename copied files + update DXF layers
                for copied_file in copied_files:
                    self.file_service.rename_one_file(
                        copied_file,
                        result,
                    )

                    current += 1
                    self.progress.emit(current, total)

            self.finished.emit(result)

            if result.errors:
                log_path = Path.home() / ".eva_logs"

                self.file_service.log_errors(
                    log_path,
                    result.errors,
                )

        except Exception as e:
            self.finished.emit(e)



