from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DxfCheckIssue:
    category: str
    message: str
    paths: list[Path] = field(default_factory=list)


@dataclass
class DxfCheckResult:
    checked_files: int = 0
    modified_files: int = 0
    issues: list[DxfCheckIssue] = field(default_factory=list)

    @property
    def problem_count(self) -> int:
        return len(self.issues)