from dataclasses import dataclass


@dataclass
class TemplateRecord:
    id: int
    folder_id: int
    template_name: str
    has_stoppers: bool

@dataclass(frozen=True)
class StopperRecord:
    id: int
    diameter: int
    stopper_name: str