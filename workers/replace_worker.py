import shutil
from PySide6.QtCore import QObject, Signal
from models.file_action_models import (
    ReplaceMode,
    ReplacePlan,
)


class ReplaceWorker(QObject):

    progress = Signal(int, int, object)
    finished = Signal(int)
    failed = Signal(str)

    def __init__(
            self,
            plan: ReplacePlan,
    ):
        super().__init__()

        self.plan = plan

    def run(self) -> None:
        try:
            total = len(self.plan.operations)
            processed = 0

            for operation in self.plan.operations:

                if self.plan.mode == ReplaceMode.MODIFY_EXISTING:
                    operation.source_file.rename(
                        operation.destination_file
                    )

                elif self.plan.mode == ReplaceMode.CREATE_COPY:
                    shutil.copy2(
                        operation.source_file,
                        operation.destination_file,
                    )

                processed += 1

                self.progress.emit(
                    processed,
                    total,
                    operation,
                )

            self.finished.emit(processed)

        except Exception as error:
            self.failed.emit(str(error))