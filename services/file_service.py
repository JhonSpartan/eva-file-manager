import pathlib
from pathlib import Path
import ezdxf
from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.results import RenameResult
    from models.results import ReplaceResult

class FileService:

    def load_files(self, directory: str) -> list[Path]:
        path = Path(directory)

        if not path.exists():
            raise ValueError("Directory does not exist")


        dxf_files = [f for f in path.rglob("*.dxf") if f.is_file()]

        return dxf_files


    # def rename_files(self, files_to_rename: list[Path]):
    #     log_path = Path(Path.home() / ".eva_logs")
    #     renamed_files = 0
    #     renamed_layers = 0
    #     odd_entries = []
    #     error_log_entries = []
    #
    #     for file in files_to_rename:
    #         renamed = False
    #         if not file.is_file():
    #             continue
    #
    #         # ожидаем структуру: EVA / ART / ID / file.dxf
    #         if len(file.parents) < 3:
    #             odd_entries.append(f"Unexpected folder depth: {file}")
    #             continue
    #
    #         file_id = file.parent.name
    #         file_art = pathlib.PurePath(file.parent.parent).name
    #         file_eva = pathlib.PurePath(file.parent.parent.parent).name
    #
    #         name = file.stem
    #         ext = file.suffix.lower()
    #
    #         if ext != ".dxf":
    #             odd_entries.append(f"Not a .dxf file detected: {file}")
    #             continue
    #
    #         if any(ch in name for ch in "óąśłźż"):
    #             odd_entries.append(f"Polish letter in {file}")
    #
    #         split_name = name.split("_")
    #
    #         if len(split_name) <= 2 or split_name[2] != file_id:
    #             split_name[2:3] = [file_id]
    #             error_log_entries.append(f"Wrong id in {file}")
    #             renamed = True
    #
    #         if len(split_name) <= 1 or split_name[1] != file_art:
    #             split_name[1:2] = [file_art]
    #             error_log_entries.append(f"Wrong art in {file}")
    #             renamed = True
    #
    #         if len(split_name) > 0 and split_name[0] != file_eva:
    #             split_name[0] = file_eva
    #             error_log_entries.append(f"Wrong EVA in {file}")
    #             renamed = True
    #
    #         rename_inner_res = self.rename_inner(file, file_art, name, file_id)
    #
    #         if rename_inner_res:
    #             renamed_layers += rename_inner_res
    #
    #         new_name = "_".join(split_name) + ext
    #         new_file = file.with_name(new_name)
    #
    #         if renamed:
    #             try:
    #                 file.rename(new_file)
    #                 renamed_files += 1
    #             except FileExistsError:
    #                 error_log_entries.append(f"Rename target exists: {new_file}")
    #             except Exception as e:
    #                 error_log_entries.append(f"Rename error for {file}: {e}")
    #
    #     if error_log_entries:
    #         self.log_errors(log_path, error_log_entries)
    #
    #     if odd_entries:
    #         self.log_errors(log_path, odd_entries)
    #
    #     error_log_entries.clear()
    #     odd_entries.clear()
    #
    #     return RenameFilesResult(
    #         renamed_files=renamed_layers,
    #         renamed_layers=renamed_layers
    #     )

    def rename_one_file(self, file: Path, result: "RenameResult") -> None:
        renamed = False

        if not file.is_file():
            return result

        # ожидаем структуру: EVA / ART / ID / file.dxf
        if len(file.parents) < 3:
            result.errors.append(f"Unexpected folder depth: {file}")
            return result

        file_id = file.parent.name
        file_art = pathlib.PurePath(file.parent.parent).name
        file_eva = pathlib.PurePath(file.parent.parent.parent).name

        name = file.stem
        ext = file.suffix.lower()

        if ext != ".dxf":
            result.errors.append(f"Not a .dxf file detected: {file}")
            return result

        if any(ch in name for ch in "óąśłźż"):
            result.errors.append(f"Polish letter in {file}")

        split_name = name.split("_")

        if len(split_name) <= 2 or split_name[2] != file_id:
            split_name[2:3] = [file_id]
            result.errors.append(f"Wrong id in {file}")
            renamed = True

        if len(split_name) <= 1 or split_name[1] != file_art:
            split_name[1:2] = [file_art]
            result.errors.append(f"Wrong art in {file}")
            renamed = True

        if len(split_name) > 0 and split_name[0] != file_eva:
            split_name[0] = file_eva
            result.errors.append(f"Wrong EVA in {file}")
            renamed = True

        rename_inner_res = self.rename_inner(file, file_art, name, file_id)

        if rename_inner_res:
            result.renamed_layers += rename_inner_res

        new_name = "_".join(split_name) + ext
        new_file = file.with_name(new_name)

        if renamed:
            try:
                file.rename(new_file)
                result.renamed_files += 1
            except FileExistsError:
                result.errors.append(f"Rename target exists: {new_file}")
            except Exception as e:
                result.errors.append(f"Rename error for {file}: {e}")

    def rename_inner(self, new_file_path: Path, file_art: str, filename: str, file_id: str) -> int:
        layer_changes = 0

        try:
            doc = ezdxf.readfile(new_file_path)
            msp = doc.modelspace()
            layers = doc.layers
        except IOError:
            print(f"Could not read the file: {new_file_path}")
        except ezdxf.DXFStructureError:
            print(f"Invalid DXF structure: {new_file_path}")
            return 0

        layer_name = "nadpis"
        layer_to_remove = "Defpoints"

        if layer_name not in layers:
            return 0

        existing_texts = [e for e in msp.query('TEXT') if e.dxf.layer == layer_name]

        if existing_texts:
            layer_change_res = self.update_existing_text(existing_texts, msp, file_art, layer_name)
        else:
            layer_change_res = self.add_new_text(doc, msp, file_art, file_id, filename, layer_name)
        layer_changes += layer_change_res

        self.remove_defpoints_layer(doc, layer_to_remove)
        self.save_file(doc, new_file_path)

        return layer_changes

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

    def remove_defpoints_layer(self, doc, layer_to_remove):
        try:
            doc.layers.remove(layer_to_remove)
        except ValueError:
            # Layer doesn't exist — ignore
            pass

    def save_file(self, doc, new_file_path):
        try:
            doc.save()
        except Exception as e:
            print(f"Error saving {new_file_path}: {e}")

    def log_errors(self, log_path, logs):
        log_path.mkdir(parents=True, exist_ok=True)
        with open(log_path / "logs.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(logs) + "\n")
        logs.clear()

    def replace_chars_in_one_file(self, file: Path, find_text: str, replace_text: str, result: "ReplaceResult") -> None:
        if not file.is_file():
            return result

        if find_text in file.name:
            new_file = file.with_name(file.name.replace(find_text, replace_text))

            try:
                file.rename(new_file)
                result.renamed += 1
            except FileExistsError:
                result.skipped.append(f"Rename target exists: {new_file}")
            except Exception as e:
                result.failed.append(f"{new_file} (Error: {e})")