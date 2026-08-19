from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto


class SelectionState(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


@dataclass
class ArtSelection:
    art_path: Path
    id_states: dict[Path, SelectionState] = field(default_factory=dict)
    files_by_id: dict[Path, list[Path]] = field(default_factory=dict)

class ValidationIssueType(Enum):
    NO_SOURCE_ART = auto()
    NO_DESTINATION_ARTS = auto()
    MISSING_DESTINATION_ID = auto()
    DESTINATION_ID_NOT_SELECTED = auto()
    ADD_FILES_WITHOUT_REPLACEMENT = auto()

class ValidationAction(Enum):
    BLOCK = auto()
    CONFIRM = auto()
    CREATE_ID = auto()

@dataclass
class CopyValidationIssue:
    issue_type: ValidationIssueType
    action: ValidationAction
    message: str
    destination_art: Path | None = None
    id_name: str | None = None

@dataclass
class CopyValidationResult:
    issues: list[CopyValidationIssue] = field(default_factory=list)

    @property
    def blocking_issues(self) -> list[CopyValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.action == ValidationAction.BLOCK
        ]

    @property
    def confirmation_issues(self) -> list[CopyValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.action == ValidationAction.CONFIRM
        ]

    @property
    def create_id_issues(self) -> list[CopyValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.action == ValidationAction.CREATE_ID
        ]

    @property
    def can_continue(self) -> bool:
        return not self.blocking_issues

@dataclass
class DestinationCopyPlan:
    destination_art: Path
    ids_to_create: list[str] = field(default_factory=list)
    files_to_delete: list[Path] = field(default_factory=list)
    copy_operations: list[FileCopyOperation] = field(default_factory=list)

@dataclass
class CopyPlan:
    source_art: Path
    destinations: list[DestinationCopyPlan] = field(
        default_factory=list
    )

    @property
    def is_empty(self) -> bool:
        for destination in self.destinations:
            if destination.ids_to_create:
                return False

            if destination.files_to_delete:
                return False

            if destination.copy_operations:
                return False

        return True

@dataclass
class FileCopyOperation:
    source_file: Path
    destination_id: Path