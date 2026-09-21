import shutil
from PySide6.QtCore import QObject, Signal
from models.file_action_models import (
    ExportLevel,
    ExportPlan,
)


class ExportWorker(QObject):

    progress = Signal(int, int, object)
    finished = Signal(int)
    failed = Signal(str)

    def __init__(
            self,
            plan: ExportPlan,
    ):
        super().__init__()

        self.plan = plan

    def run(self) -> None:

        try:
            total = len(
                self.plan.operations
            )

            processed = 0

            for operation in self.plan.operations:

                source_path = (
                    operation.source_path
                )

                destination_path = (
                    operation.destination_path
                )

                destination_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if self.plan.level == ExportLevel.FILE:

                    shutil.copy2(
                        source_path,
                        destination_path,
                    )

                else:

                    shutil.copytree(
                        source_path,
                        destination_path,
                    )

                processed += 1

                self.progress.emit(
                    processed,
                    total,
                    operation,
                )

            self.finished.emit(
                processed
            )

        except Exception as error:

            self.failed.emit(
                str(error)
            )