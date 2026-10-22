import pathlib
from pathlib import Path
import ezdxf
from ezdxf.math import Matrix44
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment
from models.results import RenameResult, RenameFileResult, ReplaceResult
import hashlib
import json
from collections import Counter
from models.dxf_check_result import DxfCheckIssue, DxfCheckResult
from services.stopper_detector import StopperDetector
from services.stopper_validator import StopperValidator


class FileService:

    def load_files(self, directory: str) -> list[Path]:
        path = Path(directory)

        if not path.exists():
            raise ValueError("Папка не существует")


        dxf_files = [f for f in path.rglob("*.dxf") if f.is_file()]

        return dxf_files

    def _file_result(
            self,
            old_path: Path,
            new_path: Path,
            renamed: bool,
    ) -> RenameFileResult:
        return RenameFileResult(
            old_path=old_path,
            new_path=new_path,
            renamed=renamed,
        )

    def get_dxf_files(self, art_path: Path) -> list[Path]:
        files = []

        if not art_path.is_dir():
            return files

        for id_folder in art_path.iterdir():
            if not id_folder.is_dir():
                continue

            for file in id_folder.iterdir():
                if not file.is_file():
                    continue

                if file.suffix.lower() != ".dxf":
                    continue

                files.append(file)

        return sorted(files, key=lambda path: str(path))

    def rename_one_file(self, file: Path, result: RenameResult) -> RenameFileResult:
        renamed = False
        need_rename = False
        new_file = file

        if not file.is_file():
            return self._file_result(file, new_file, False)

        # ожидаем структуру: EVA / ART / ID / file.dxf
        if len(file.parents) < 3:
            result.errors.append(f"Некорректная глубина папок: {file}")
            return self._file_result(file, new_file, False)

        file_id = file.parent.name
        file_art = pathlib.PurePath(file.parent.parent).name
        file_eva = pathlib.PurePath(file.parent.parent.parent).name

        name = file.stem
        ext = file.suffix.lower()

        if ext != ".dxf":
            result.errors.append(f"Обнаружен файл не в формате .dxf: {file}")
            return self._file_result(file, new_file, False)

        if any(ch in name for ch in "óąśłźż"):
            result.errors.append(f"Польская буква в файле {file}")

        split_name = name.split("_")

        if len(split_name) <= 2 or split_name[2] != file_id:
            split_name[2:3] = [file_id]
            result.errors.append(f"Некорректный ID в файле {file}")
            need_rename = True

        if len(split_name) <= 1 or split_name[1] != file_art:
            split_name[1:2] = [file_art]
            result.errors.append(f"Некорректный ART в файле {file}")
            need_rename = True

        if len(split_name) > 0 and split_name[0] != file_eva:
            split_name[0] = file_eva
            result.errors.append(f"Некорректная EVA в файле {file}")
            need_rename = True

        rename_inner_res = self.rename_inner(file, file_art, name, file_id, result)

        if rename_inner_res:
            result.renamed_layers += rename_inner_res

        new_name = "_".join(split_name) + ext
        new_file = file.with_name(new_name)

        if need_rename:
            try:
                file.rename(new_file)

                renamed = True
                result.renamed_files += 1
            except FileExistsError:
                result.errors.append(f"Целевой файл уже существует: {new_file}")
            except Exception as e:
                result.errors.append(f"Ошибка переименования файла {file}: {e}")

        return self._file_result(file, new_file, renamed)

    def add_centered_nadpis(self, doc, msp, file_art: str) -> bool:
        main_entities = [
            entity for entity in msp
            if entity.dxf.layer.lower() == "main"
        ]

        if not main_entities:
            return False

        bounds = bbox.extents(main_entities)

        if not bounds.has_data:
            return False

        center_x = (bounds.extmin.x + bounds.extmax.x) / 2
        center_y = (bounds.extmin.y + bounds.extmax.y) / 2

        if "MyTextStyle" not in doc.styles:
            doc.styles.new(
                name="MyTextStyle",
                dxfattribs={
                    "font": "arial.ttf",
                    "width": 1.0,
                },
            )

        doc.layers.new(name="nadpis")

        text = msp.add_text(
            file_art,
            dxfattribs={
                "layer": "nadpis",
                "height": 2.0,
                "color": 5,
                "style": "MyTextStyle",
            },
        )

        text.set_placement(
            (center_x, center_y),
            align=TextEntityAlignment.MIDDLE_CENTER,
        )

        return True

    def check_dxf_main(self, file: Path) -> str | None:
        try:
            doc = ezdxf.readfile(file)
        except (OSError, ezdxf.DXFStructureError) as e:
            return f"Не удалось прочитать DXF: {file} ({e})"

        if "main" not in doc.layers:
            return f"Отсутствует обязательный слой main: {file}"

        return None

    def rename_inner(
            self,
            new_file_path: Path,
            file_art: str,
            filename: str,
            file_id: str,
            result: RenameResult,
    ) -> int:
        try:
            doc = ezdxf.readfile(new_file_path)
            msp = doc.modelspace()
            layers = doc.layers

        except (IOError, ezdxf.DXFStructureError):
            return 0

        # Без main DXF не изменяем и не сохраняем.
        if "main" not in layers:
            return 0

        layer_changes = 0

        units_normalized = self.normalize_insunits(doc)

        if "nadpis" not in layers:
            if self.add_centered_nadpis(doc, msp, file_art):
                layer_changes += 1

        else:
            existing_texts = [
                entity for entity in msp.query("TEXT")
                if entity.dxf.layer == "nadpis"
            ]

            if existing_texts:
                layer_changes += self.update_existing_text(
                    existing_texts,
                    msp,
                    file_art,
                    "nadpis",
                )
            else:
                layer_changes += self.add_new_text(
                    doc,
                    msp,
                    file_art,
                    file_id,
                    filename,
                    "nadpis",
                )

        # Удаление Defpoints тоже считается изменением.
        defpoints_exists = "Defpoints" in layers

        if defpoints_exists:
            self.remove_defpoints_layer(doc, "Defpoints")

        if units_normalized or layer_changes or defpoints_exists:
            self.save_file(doc)

            if units_normalized:
                result.normalized_units += 1

            if layer_changes:
                result.renamed_layers += layer_changes

        return 0

    def update_existing_text(self, existing_texts, msp, file_art, layer_name):
        layer_changes = 0

        for entity in existing_texts:
            if entity.dxf.text and entity.dxf.text.split("_")[0] == file_art:
                return 0

        for entity in existing_texts:
            text = entity.dxf.text
            split_txt = text.split("_")
            if not split_txt:
                continue

            split_txt[0] = file_art
            new_text = "_".join(split_txt)
            insert = entity.dxf.insert
            color = entity.dxf.color
            style = entity.dxf.style
            height = entity.dxf.height

            msp.delete_entity(entity)

            msp.add_text(new_text,
                         dxfattribs={"layer": layer_name, "height": height, "color": color, "style": style,
                                     "insert": insert})
            layer_changes += 1

        return layer_changes

    def add_new_text(self, doc, msp, file_art, file_id, filename, layer_name):
        layer_changes = 0

        leftmost_x = float('inf')
        topmost_y = float('-inf')

        if 'MyTextStyle' not in doc.styles:
            doc.styles.new(name='MyTextStyle', dxfattribs={
                'font': 'arial.ttf',
                'width': 1.0,
            })

        added_word = file_art
        trunk_word_list = ["_short", "_long", "_upper", "_lower"]
        others_word_list = ["_left", "_right"]

        if file_id in ("12", "13", "14"):
            for word in trunk_word_list:
                if word in filename:
                    added_word += word
                    break
        else:
            for word in others_word_list:
                if word in filename:
                    added_word += word
                    break

        for entity in msp.query('SPLINE'):
            if entity.dxf.layer == layer_name:
                for pt in entity.control_points:
                    x, y, z = pt
                    if x < leftmost_x:
                        leftmost_x = x
                    if y > topmost_y:
                        topmost_y = y
                msp.delete_entity(entity)

        if leftmost_x != float('inf') and topmost_y != float('-inf'):
            msp.add_text(added_word,
                         dxfattribs={"layer": layer_name, "height": 2.0, "color": 5, "style": "MyTextStyle",
                                     "insert": (leftmost_x, topmost_y, 0.0)})
            layer_changes += 1

        return layer_changes

    def normalize_insunits(self, doc) -> bool:
        """Исправляет ошибочный экспорт DXF с INSUNITS=1."""
        insunits = doc.header.get("$INSUNITS")

        if insunits != 1:
            return False

        msp = doc.modelspace()
        transform = Matrix44.scale(2.54, 2.54, 2.54)

        for entity in msp:
            entity.transform(transform)

        doc.header["$INSUNITS"] = 5

        return True

    def remove_defpoints_layer(self, doc, layer_to_remove):
        try:
            doc.layers.remove(layer_to_remove)
        except ValueError:
            # Слой не существует — игнорируем
            pass

    def save_file(self, doc):
        doc.save()

    def log_errors(self, log_path, logs):
        log_path.mkdir(parents=True, exist_ok=True)
        with open(log_path / "logs.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(logs) + "\n")
        logs.clear()

    def replace_chars_in_one_file(self, file: Path, find_text: str, replace_text: str, result: ReplaceResult) -> RenameFileResult:
        renamed = False

        if not file.is_file():
            return self._file_result(file, file, False)

        if find_text not in file.stem:
            return self._file_result(file, file, False)

        new_name = file.stem.replace(find_text, replace_text) + file.suffix
        new_file = file.with_name(new_name)

        try:
            file.rename(new_file)

            renamed = True
            result.renamed += 1
        except FileExistsError:
            result.skipped.append(f"Целевой файл уже существует: {new_file}")
        except Exception as e:
            result.failed.append(f"{new_file} (Ошибка: {e})")

        return self._file_result(file, new_file, renamed)

    def collect_dxf_files(
            self,
            paths: list[Path],
    ) -> list[Path]:

        result = []

        for path in paths:
            if path.is_file():
                if path.suffix.lower() == ".dxf":
                    result.append(path)

            elif path.is_dir():
                result.extend(
                    file_path
                    for file_path in path.rglob("*.dxf")
                    if file_path.is_file()
                )

        return result

    def _get_main_geometry_hash(self, file: Path) -> str | None:
        doc = ezdxf.readfile(file)
        msp = doc.modelspace()

        splines = []

        def normalize(values):
            return [round(float(value), 5) for value in values]

        main_splines = [
            entity
            for entity in msp.query("SPLINE")
            if entity.dxf.layer.lower() == "main"
        ]

        if not main_splines:
            return None

        # Общая точка отсчёта для всех SPLINE файла.
        all_points = [
            point
            for entity in main_splines
            for point in entity.control_points
        ]

        if not all_points:
            return None

        origin = (
            min(point[0] for point in all_points),
            min(point[1] for point in all_points),
            min(point[2] for point in all_points),
        )

        for entity in main_splines:
            relative_points = [
                [
                    round(float(value - start), 5)
                    for value, start in zip(point, origin)
                ]
                for point in entity.control_points
            ]

            spline_data = {
                "degree": entity.dxf.degree,
                "flags": entity.dxf.flags,
                "control_points": relative_points,
                "knots": normalize(entity.knots),
                "weights": normalize(entity.weights),
            }

            splines.append(spline_data)

        splines.sort(
            key=lambda spline: json.dumps(
                spline,
                sort_keys=True,
            )
        )

        data = json.dumps(
            splines,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _find_matching_geometry(
            self,
            files_1: list[Path],
            files_2: list[Path],
    ) -> list[tuple[Path, Path]]:
        hashes_2 = {}

        for file in files_2:
            geometry_hash = self._get_main_geometry_hash(file)
            if geometry_hash is not None:
                hashes_2.setdefault(geometry_hash, []).append(file)

        matches = []

        for file in files_1:
            geometry_hash = self._get_main_geometry_hash(file)

            if geometry_hash is None:
                continue

            for matching_file in hashes_2.get(geometry_hash, []):
                matches.append((file, matching_file))

        return matches

    def _find_unmatched_geometry(
            self,
            files_1: list[Path],
            files_2: list[Path],
    ) -> tuple[list[Path], list[Path]]:
        hashes_1 = {}
        hashes_2 = {}

        for file in files_1:
            geometry_hash = self._get_main_geometry_hash(file)
            if geometry_hash is not None:
                hashes_1.setdefault(geometry_hash, []).append(file)

        for file in files_2:
            geometry_hash = self._get_main_geometry_hash(file)
            if geometry_hash is not None:
                hashes_2.setdefault(geometry_hash, []).append(file)

        unmatched_1 = []
        unmatched_2 = []

        for geometry_hash in hashes_1.keys() | hashes_2.keys():
            group_1 = hashes_1.get(geometry_hash, [])
            group_2 = hashes_2.get(geometry_hash, [])

            common_count = min(len(group_1), len(group_2))

            unmatched_1.extend(group_1[common_count:])
            unmatched_2.extend(group_2[common_count:])

        return sorted(unmatched_1), sorted(unmatched_2)

    def _find_unmatched_passengers(
            self,
            passengers_1: list[Path],
            passengers_2: list[Path],
    ) -> tuple[list[Path], list[Path]]:

        def variant(file: Path) -> str:
            return file.stem.lower().split("_passenger", 1)[1]

        groups_1 = {variant(file): file for file in passengers_1}
        groups_2 = {variant(file): file for file in passengers_2}

        unmatched_1 = []
        unmatched_2 = []

        for suffix in sorted(groups_1.keys() | groups_2.keys()):
            file_1 = groups_1.get(suffix)
            file_2 = groups_2.get(suffix)

            if file_1 is None:
                unmatched_2.append(file_2)
            elif file_2 is None:
                unmatched_1.append(file_1)
            else:
                hash_1 = self._get_main_geometry_hash(file_1)
                hash_2 = self._get_main_geometry_hash(file_2)

                if hash_1 is not None and hash_2 is not None:
                    if hash_1 != hash_2:
                        unmatched_1.append(file_1)
                        unmatched_2.append(file_2)

        return unmatched_1, unmatched_2

    def _find_duplicate_geometry(
            self, files: list[Path],
    ) -> list[tuple[Path, Path]]:
        duplicates = []
        hashes = {}

        for file in files:
            geometry_hash = self._get_main_geometry_hash(file)

            if geometry_hash is None:
                continue

            if geometry_hash in hashes:
                duplicates.append((hashes[geometry_hash], file))
            else:
                hashes[geometry_hash] = file

        return duplicates

    def get_art_passengers(
            self, art_dir: Path,
    ) -> tuple[list[Path], list[Path]]:
        def collect(id_number: int) -> list[Path]:
            id_dir = art_dir / str(id_number)

            if not id_dir.is_dir():
                return []

            return sorted(
                file
                for file in id_dir.iterdir()
                if file.is_file()
                and file.suffix.lower() == ".dxf"
                and "passenger" in file.stem.lower().split("_")
                and "driver_with_passenger" not in file.stem.lower()
            )

        return collect(1), collect(2)

    def get_art_drivers(
            self, art_dir: Path,
    ) -> tuple[list[Path], list[Path]]:
        def collect(id_number: int) -> list[Path]:
            id_dir = art_dir / str(id_number)

            if not id_dir.is_dir():
                return []

            return sorted(
                file
                for file in id_dir.iterdir()
                if file.is_file()
                and file.suffix.lower() == ".dxf"
                and "driver" in file.stem.lower().split("_")
                and "driver_with_passenger" not in file.stem.lower()
            )

        return collect(1), collect(2)

    def get_art_combined(
            self, art_dir: Path,
    ) -> tuple[list[Path], list[Path]]:

        def collect(id_number: int) -> list[Path]:
            id_dir = art_dir / str(id_number)

            if not id_dir.is_dir():
                return []

            return sorted(
                file
                for file in id_dir.iterdir()
                if file.is_file()
                and file.suffix.lower() == ".dxf"
                and "driver_with_passenger" in file.stem.lower()
            )

        return collect(1), collect(2)

    def check_art_geometry(self, art_dir: Path) -> DxfCheckResult:
        result = DxfCheckResult()

        passengers_1, passengers_2 = self.get_art_passengers(art_dir)
        drivers_1, drivers_2 = self.get_art_drivers(art_dir)
        combined_1, combined_2 = self.get_art_combined(art_dir)

        for label, files in [
            ("Driver ID1", drivers_1),
            ("Driver ID2", drivers_2),
            ("Passenger ID1", passengers_1),
            ("Passenger ID2", passengers_2),
            ("Combined ID1", combined_1),
            ("Combined ID2", combined_2),
        ]:
            duplicates = self._find_duplicate_geometry(files)

            for file_1, file_2 in duplicates:
                result.issues.append(
                    DxfCheckIssue(
                        category="geometry_duplicate_within_id",
                        message=f"Совпадает геометрия внутри {label}: {art_dir}",
                        paths=[file_1, file_2],
                    )
                )

        # Совпадения Combined между ID1 и ID2
        combined_matches = self._find_matching_geometry(
            combined_1, combined_2
        )

        for file_1, file_2 in combined_matches:
            result.issues.append(
                DxfCheckIssue(
                    category="combined_duplicate_between_ids",
                    message=f"Совпадает геометрия Combined ID1 и ID2: {art_dir}",
                    paths=[file_1, file_2],
                )
            )

        # 1. Passenger ID1 ↔ ID2
        # 1. Passenger ID1 ↔ ID2
        if (art_dir / "1").is_dir():
            unmatched_1, unmatched_2 = self._find_unmatched_passengers(
                passengers_1, passengers_2
            )

            if unmatched_1 or unmatched_2:
                result.issues.append(
                    DxfCheckIssue(
                        category="passenger_mismatch",
                        message=(
                            f"Несоответствие геометрии Passenger "
                            f"между ID1 и ID2: {art_dir}"
                        ),
                        paths=unmatched_1 + unmatched_2,
                    )
                )

        # 2. Driver ID1 ↔ ID2
        driver_matches = self._find_matching_geometry(
            drivers_1, drivers_2
        )

        for file_1, file_2 in driver_matches:
            result.issues.append(
                DxfCheckIssue(
                    category="driver_duplicate",
                    message=f"Совпадает геометрия Driver ID1 и ID2: {art_dir}",
                    paths=[file_1, file_2],
                )
            )

        # 3. Driver ↔ Passenger внутри ART
        all_drivers = drivers_1 + drivers_2
        all_passengers = passengers_1 + passengers_2

        cross_matches = self._find_matching_geometry(
            all_drivers, all_passengers
        )

        for driver, passenger in cross_matches:
            result.issues.append(
                DxfCheckIssue(
                    category="driver_passenger_match",
                    message=f"Совпадает геометрия Driver и Passenger: {art_dir}",
                    paths=[driver, passenger],
                )
            )

        return result

    def check_file_stoppers(
            self,
            file_path: Path,
            expected_diameter: float,
            standard_diameters: list[float],
    ) -> DxfCheckResult:

        result = DxfCheckResult(checked_files=1)

        try:
            doc = ezdxf.readfile(file_path)
        except (OSError, ezdxf.DXFStructureError) as error:
            result.issues.append(
                DxfCheckIssue(
                    category="stopper_read_error",
                    message=f"Не удалось прочитать DXF: {error}",
                    paths=[file_path],
                )
            )
            return result

        detector = StopperDetector()
        validator = StopperValidator()

        candidates = detector.find_candidates(doc.modelspace())

        min_size = min(standard_diameters) - validator.DIAMETER_TOLERANCE_MM
        max_size = max(standard_diameters) + validator.DIAMETER_TOLERANCE_MM

        stopper_candidates = [
            candidate
            for candidate in candidates
            if (
                    min_size <= candidate.width * validator.DXF_TO_MM <= max_size
                    and min_size <= candidate.height * validator.DXF_TO_MM <= max_size
            )
        ]

        if not stopper_candidates:
            result.issues.append(
                DxfCheckIssue(
                    category="stopper_missing",
                    message=(
                        f"Стоперы не обнаружены. "
                        f"Ожидаемый диаметр: {expected_diameter:g} мм. "
                        f"Проверьте наличие стоперов и название файла."
                    ),
                    paths=[file_path],
                )
            )
            return result

        for candidate in stopper_candidates:
            validation = validator.validate(candidate, expected_diameter)

            if validation.is_valid:
                continue

            width_mm = candidate.width * validator.DXF_TO_MM
            height_mm = candidate.height * validator.DXF_TO_MM

            message = (
                f"Несоответствие диаметра стопера: "
                f"ожидалось {expected_diameter:g} мм, "
                f"обнаружено {width_mm:.2f} × {height_mm:.2f} мм."
            )

            for diameter in standard_diameters:
                if diameter == expected_diameter:
                    continue

                if (
                        abs(width_mm - diameter) <= validator.DIAMETER_TOLERANCE_MM
                        and abs(height_mm - diameter) <= validator.DIAMETER_TOLERANCE_MM
                ):
                    message += (
                        f" Совпадает с другим стандартным "
                        f"номиналом: {diameter:g} мм."
                    )
                    break

            result.issues.append(
                DxfCheckIssue(
                    category="stopper_diameter_mismatch",
                    message=message,
                    paths=[file_path],
                )
            )

        return result





