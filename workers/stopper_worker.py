from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot
from services.stopper_editor import StopperEditor


class StopperWorker(QObject):
    progress = Signal(int, int, object, bool)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(
            self,
            editor: StopperEditor,
            files: list[Path],
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
            changed_files = 0
            deleted_files = 0

            total_files = len(
                self.files
            )

            for index, file_path in enumerate(
                    self.files,
                    start=1,
            ):
                modified = False

                try:
                    if self.action == "change":
                        result = self.editor.change_diameter(
                            file_path=file_path,
                            expected_diameter=self.expected_diameter,
                            new_diameter=self.new_diameter,
                        )

                        changed_total += result.changed_count

                        modified = (
                                result.changed_count > 0
                        )

                        if modified:
                            changed_files += 1

                    elif self.action == "delete":
                        result = self.editor.delete_stoppers(
                            file_path=file_path,
                            expected_diameter=self.expected_diameter,
                        )

                        deleted_total += result.deleted_count

                        modified = (
                                result.deleted_count > 0
                        )

                        if modified:
                            deleted_files += 1

                    else:
                        raise ValueError(
                            f"Unknown stopper action: "
                            f"{self.action}"
                        )

                    processed_files += 1

                except Exception:
                    failed_files += 1

                self.progress.emit(
                    index,
                    total_files,
                    file_path,
                    modified,
                )

            self.finished.emit(
                {
                    "processed_files": processed_files,
                    "failed_files": failed_files,
                    "changed_total": changed_total,
                    "changed_files": changed_files,
                    "deleted_total": deleted_total,
                    "deleted_files": deleted_files,
                }
            )

        except Exception as error:
            self.failed.emit(
                str(error)
            )