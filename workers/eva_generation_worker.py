from PySide6.QtCore import QObject, Signal, Slot
from models.eva_models import GenerationPlan


class EvaGenerationWorker(QObject):

    progressChanged = Signal(int)
    finished = Signal(int, int)
    failed = Signal(str)

    def __init__(
            self,
            generation_plan: GenerationPlan,
    ):
        super().__init__()

        self.generation_plan = generation_plan

    @Slot()
    def run(self):
        try:
            total_files = (
                self.generation_plan
                .total_files
            )

            if total_files == 0:
                self.progressChanged.emit(100)
                self.finished.emit(0, 0)
                return

            created_count = 0
            existing_count = 0

            for index, generation_file in enumerate(
                    self.generation_plan.files,
                    start=1,
            ):
                destination_file = (
                    generation_file
                    .destination_file
                )

                destination_file.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if destination_file.exists():
                    existing_count += 1
                else:
                    destination_file.touch()
                    created_count += 1

                progress = int(
                    index
                    / total_files
                    * 100
                )

                self.progressChanged.emit(
                    progress
                )

            self.finished.emit(
                created_count,
                existing_count,
            )

        except Exception as error:
            self.failed.emit(
                str(error)
            )