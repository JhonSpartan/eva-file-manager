from pathlib import Path


class ArtService:

    def load_arts(self, directory: str) -> list[Path]:
        root = Path(directory)

        if not root.exists():
            raise ValueError("Папка не существует")

        # Если выбран непосредственно ART
        if self._contains_dxf(root):
            return [root]

        children = [p for p in root.iterdir() if p.is_dir()]

        if not children:
            return []

        arts = []

        for child in children:
            if self._contains_dxf(child):
                arts.append(child)
                continue

            for art in child.iterdir():
                if art.is_dir() and self._contains_dxf(art):
                    arts.append(art)

        return arts

    def _contains_dxf(self, folder: Path) -> bool:
        for subdir in (p for p in folder.iterdir() if p.is_dir()):

            if any(
                    file.is_file() and file.suffix.lower() == ".dxf"
                    for file in subdir.iterdir()
            ):
                return True

        return False

    def collect_arts(
            self,
            paths: list[Path],
    ) -> list[Path]:

        arts = []
        seen = set()

        for path in paths:
            if not path.is_dir():
                continue

            for art_path in self.load_arts(
                    str(path)
            ):
                if art_path in seen:
                    continue

                arts.append(art_path)
                seen.add(art_path)

        return arts

