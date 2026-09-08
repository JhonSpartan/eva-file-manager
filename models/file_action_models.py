from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto


class ReplaceMode(Enum):
    MODIFY_EXISTING = auto()
    CREATE_COPY = auto()

class ExportLevel(Enum):
    FILE = auto()
    ART = auto()
    EVA = auto()

class DeleteLevel(Enum):
    FILE = auto()
    ID=auto()
    ART = auto()
    EVA = auto()

@dataclass
class ReplaceOperation:
    source_file: Path
    destination_file: Path


@dataclass
class ReplacePlan:
    find_text: str
    replace_text: str
    mode: ReplaceMode
    operations: list[ReplaceOperation] = field(
        default_factory=list
    )
    conflicts: list[Path] = field(
        default_factory=list
    )

    @property
    def is_empty(self) -> bool:
        return not self.operations

@dataclass
class ExportOperation:
    source_path: Path
    destination_path: Path


@dataclass
class ExportPlan:
    level: ExportLevel
    destination_root: Path
    operations: list[ExportOperation] = field(
        default_factory=list
    )
    conflicts: list[Path] = field(
        default_factory=list
    )

    @property
    def is_empty(self) -> bool:
        return not self.operations


@dataclass
class DeleteOperation:
    target_path: Path


@dataclass
class DeletePlan:
    level: DeleteLevel
    operations: list[DeleteOperation] = field(
        default_factory=list
    )

    @property
    def is_empty(self) -> bool:
        return not self.operations

@dataclass
class MoveFileOperation:
    source_file: Path
    destination_file: Path


@dataclass
class MoveToIdPlan:
    destination_id: str
    operations: list[MoveFileOperation] = field(
        default_factory=list
    )
    source_id_paths: set[Path] = field(
        default_factory=set
    )
    conflicts: list[Path] = field(
        default_factory=list
    )

    @property
    def is_empty(self) -> bool:
        return not self.operations

