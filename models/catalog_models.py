from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateRecord:
    id: int
    folder_id: int
    template_name: str