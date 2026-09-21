from pathlib import Path
import shutil


class ArtCopyService:

    def copy_file(
            self,
            source_file: Path,
            destination_file: Path,
    ):
        shutil.copy2(
            source_file,
            destination_file,
        )