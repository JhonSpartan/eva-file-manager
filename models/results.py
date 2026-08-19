from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class RenameFileResult:
    old_path: Path
    new_path: Path
    renamed: bool

@dataclass
class RenameResult:
    renamed_files: int = 0
    renamed_layers: int = 0
    errors: list[str] = field(default_factory=list)

@dataclass
class ReplaceResult:
    renamed: int = 0
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

@dataclass
class CopyArtResult:
    created_ids: int = 0
    deleted_files: int = 0
    copied_files: int = 0
    renamed_files: int = 0
    renamed_layers: int = 0
    errors: list[str] = field(default_factory=list)

