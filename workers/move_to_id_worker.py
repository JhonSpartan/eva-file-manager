from PySide6.QtCore import (
    QObject,
    Signal,
)

from models.file_action_models import (
    MoveToIdPlan,
)


class MoveToIdWorker(QObject):

    progress = Signal(int, int, object)
    finished = Signal(int)
    errorOccurred = Signal(str)

    def __init__(
            self,
            plan: MoveToIdPlan,
    ):
        super().__init__()

        self.plan = plan

    def run(self) -> None:

        try:
            total = len(
                self.plan.operations
            )

            processed = 0

            # 1. Move files

            for operation in self.plan.operations:

                destination_file = (
                    operation.destination_file
                )

                destination_file.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                operation.source_file.rename(
                    destination_file
                )

                processed += 1

                self.progress.emit(
                    processed,
                    total,
                    operation,
                )

            # 2. Remove empty source ID folders

            for source_id_path in (
                    self.plan.source_id_paths
            ):

                if not source_id_path.exists():
                    continue

                if not source_id_path.is_dir():
                    continue

                if any(source_id_path.iterdir()):
                    continue

                source_id_path.rmdir()

            self.finished.emit(
                processed
            )

        except Exception as error:

            self.errorOccurred.emit(
                str(error)
            )