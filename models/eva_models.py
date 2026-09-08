from dataclasses import dataclass, field
from models.catalog_models import StopperRecord
from enum import Enum, auto
from pathlib import Path

@dataclass
class PreparedEva:
    name: str
    articles: list[str]

@dataclass
class StopperCombination:
    stoppers: list[StopperRecord]

    @property
    def name(self) -> str:
        return "_".join(
            stopper.stopper_name
            for stopper in self.stoppers
        )

    @property
    def diameter(self) -> float:
        return self.stoppers[0].diameter


class TemplateOrigin(Enum):
    DATABASE = auto()
    STOPPER = auto()
    CUSTOM = auto()

@dataclass
class SessionTemplate:
    folder_id: int
    template_name: str
    origin: TemplateOrigin
    has_stoppers: bool = False
    selected: bool = False
    stopper_combination: StopperCombination | None = None

@dataclass
class PreviewTemplate:
    destination_folder_id: int
    template_name: str

@dataclass
class GenerationFile:
    eva_name: str
    article: str
    destination_folder_id: int
    template_name: str
    destination_file: Path
    stopper_combination: StopperCombination | None = None

@dataclass
class GenerationPlan:
    destination_root: Path
    files: list[GenerationFile] = field(
        default_factory=list
    )

    @property
    def is_empty(self) -> bool:
        return not self.files

    @property
    def total_files(self) -> int:
        return len(self.files)