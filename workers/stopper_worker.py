from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from services.stopper_editor import StopperEditor


class StopperWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(
            self,
            editor: StopperEditor,
            files: list[str],
            action: str,
            expected_diameter: float,
            new_diameter: float | None = None,
    ):
        super().__init__()

        self.editor = editor
        self.files = files
        self.action = action
        self.expected_diameter = expected_diameter
        self.new_diameter = new_diameter

    @Slot()
    def run(self) -> None:
        try:
            processed_files = 0
            failed_files = 0
            changed_total = 0
            deleted_total = 0

            total_files = len(
                self.files
            )

            for index, file_path in enumerate(
                    self.files,
                    start=1,
            ):
                try:
                    if self.action == "change":
                        result = (
                            self.editor
                            .change_diameter(
                                file_path=Path(file_path),
                                expected_diameter=(
                                    self.expected_diameter
                                ),
                                new_diameter=(
                                    self.new_diameter
                                ),
                            )
                        )

                        changed_total += (
                            result.changed_count
                        )

                    elif self.action == "delete":
                        result = (
                            self.editor
                            .delete_stoppers(
                                file_path=Path(file_path),
                                expected_diameter=(
                                    self.expected_diameter
                                ),
                            )
                        )

                        deleted_total += (
                            result.deleted_count
                        )

                    else:
                        raise ValueError(
                            f"Unknown stopper action: "
                            f"{self.action}"
                        )

                    processed_files += 1

                except Exception as error:
                    failed_files += 1

                    print(
                        "Stopper operation failed:",
                        file_path,
                        error,
                    )

                self.progress.emit(
                    index,
                    total_files,
                )

            self.finished.emit(
                {
                    "processed_files": (
                        processed_files
                    ),
                    "failed_files": (
                        failed_files
                    ),
                    "changed_total": (
                        changed_total
                    ),
                    "deleted_total": (
                        deleted_total
                    ),
                }
            )

        except Exception as error:
            self.failed.emit(
                str(error)
            )