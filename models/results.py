from dataclasses import dataclass, field

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
