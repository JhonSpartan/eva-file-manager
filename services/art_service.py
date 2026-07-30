from pathlib import Path

class ArtService:

    def load_arts(self, directory: str) -> list[Path]:
        root = Path(directory)

        if not root.exists():
            raise ValueError("Directory does not exist")

        children = [p for p in root.iterdir() if p.is_dir()]

        if not children:
            return []

        first = children[0]

        if self._contains_dxf(first):
            return children

        arts = []

        for eva in children:
            arts.extend(
                art for art in eva.iterdir()
                if art.is_dir()
            )

        return arts

    def _contains_dxf(self, folder: Path) -> bool:
        for subdir in (p for p in folder.iterdir() if p.is_dir()):

            if any(
                    file.is_file() and file.suffix.lower() == ".dxf"
                    for file in subdir.iterdir()
            ):
                return True

        return False
