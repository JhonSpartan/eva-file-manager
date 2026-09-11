from dataclasses import dataclass


@dataclass
class StopperEditResult:
    deleted_count: int = 0
    changed_count: int = 0