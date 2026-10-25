from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from models.dxf_check_result import DxfCheckResult
from services.file_service import FileService


class DxfCheckWorker(QObject):
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(list, list, object, object, list)
    failed = Signal(str)

    def __init__(
        self,
        visible_files: list[Path],
        file_service: FileService,
        stopper_data: dict[str, float],
        standard_diameters: list[float],
        art_directories: list[Path],
        eva_directories: list[Path],
    ):
        super().__init__()
        self.visible_files = visible_files.copy()
        self.stopper_data = stopper_data.copy()
        self.standard_diameters = standard_diameters.copy()
        self.art_directories = art_directories.copy()
        self.eva_directories = eva_directories.copy()
        self.file_service = file_service

    @Slot()
    def run(self):
        missing_main = []
        read_errors = []
        empty_id_directories = []
        stopper_result = DxfCheckResult()
        geometry_result = DxfCheckResult()
        total = (
                len(self.visible_files) * 2
                + len(self.art_directories)
                + len(self.eva_directories)
        )
        current = 0

        try:
            for file in self.visible_files:
                self.status.emit(f"Проверка стопперов: {file.name}")

                stopper_name = file.stem.lower().rsplit("_", 1)[-1]
                expected_diameter = self.stopper_data.get(stopper_name)

                if expected_diameter is not None:
                    file_result = self.file_service.check_file_stoppers(
                        file_path=file,
                        expected_diameter=expected_diameter,
                        standard_diameters=self.standard_diameters,
                    )

                    stopper_result.checked_files += file_result.checked_files
                    stopper_result.issues.extend(file_result.issues)

                current += 1
                self.progress.emit(current, total)

            for file in self.visible_files:
                self.status.emit(f"Проверка слоя main: {file.name}")

                error = self.file_service.check_dxf_main(file)

                if error:
                    if error.startswith("Не удалось прочитать DXF"):
                        read_errors.append(error)
                    else:
                        missing_main.append(error)

                current += 1
                self.progress.emit(current, total)

            for art_dir in self.art_directories:
                self.status.emit(
                    f"Проверка геометрии: {art_dir.parent.name} / {art_dir.name}"
                )

                art_result = self.file_service.check_art_geometry(art_dir)
                geometry_result.issues.extend(art_result.issues)

                current += 1
                self.progress.emit(current, total)

            for eva_dir in self.eva_directories:
                self.status.emit(f"Проверка пустых ID: {eva_dir.name}")

                for art_dir in eva_dir.iterdir():
                    if not art_dir.is_dir():
                        continue

                    for id_dir in art_dir.iterdir():
                        if not id_dir.is_dir():
                            continue

                        if not id_dir.name.isdigit():
                            continue

                        if not any(id_dir.iterdir()):
                            empty_id_directories.append(id_dir)

                current += 1
                self.progress.emit(current, total)

        except Exception as error:
            self.failed.emit(str(error))
            return

        self.finished.emit(
            missing_main,
            read_errors,
            stopper_result,
            geometry_result,
            sorted(empty_id_directories),
        )