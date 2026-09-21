import shutil
from PySide6.QtCore import (
    QObject,
    Signal,
)
from models.file_action_models import (
    DeleteLevel,
    DeletePlan,
)


class DeleteWorker(QObject):

    progress = Signal(int, int, object)
    finished = Signal(int)
    errorOccurred = Signal(str)

    def __init__(
            self,
            plan: DeletePlan,
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

                target_path = (
                    operation.target_path
                )

                if self.plan.level == DeleteLevel.FILE:
                    target_path.unlink()

                else:
                    shutil.rmtree(
                        target_path
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
            self.errorOccurred.emit(
                str(error)
            )