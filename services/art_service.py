import pathlib
from pathlib import Path

class ArtService:

    def load_arts(self, directory: str) -> list[Path]:
        path = Path(directory)

        if not path.exists():
            raise ValueError("Directory does not exist")


        # arts = [d for d in path.rglob("*.dxf").parents[1] if d.is_dir()]
        arts = []
        root = Path(directory)

        for eva in root.iterdir():
            if not eva.is_dir():
                continue

            for art in eva.iterdir():
                if art.is_dir():
                    arts.append(art)

        return arts
