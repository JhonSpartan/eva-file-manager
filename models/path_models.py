from dataclasses import dataclass
from pathlib import Path


@dataclass
class PathRecord:
    id: int | None
    key: str
    path: Path | None