from pathlib import Path
import shutil


class ArtCopyService:

    def clear_art(self, art_path: Path):
        """Удаляет всё содержимое ART, но оставляет саму папку."""

        if not art_path.is_dir():
            raise ValueError(f"ART directory does not exist: {art_path}")

        for item in art_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def copy_art(
            self,
            source_art: Path,
            destination_art: Path,
    ):
        """Копирует всё содержимое одного ART в другой ART."""

        if not source_art.is_dir():
            raise ValueError(
                f"Source ART does not exist: {source_art}"
            )

        if not destination_art.is_dir():
            raise ValueError(
                f"Destination ART does not exist: {destination_art}"
            )

        self.clear_art(destination_art)

        for item in source_art.iterdir():
            destination = destination_art / item.name

            if item.is_dir():
                shutil.copytree(item, destination)
            else:
                shutil.copy2(item, destination)