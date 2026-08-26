from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateRecord:
    id: int
    folder_id: int
    template_name: str

@dataclass(frozen=True)
class StopperRecord:
    id: int
    diameter: int
    stopper_name: str