from dataclasses import dataclass

from ezdxf.entities import DXFGraphic
from ezdxf.path import Path


@dataclass
class StopperCandidate:
    entity: DXFGraphic
    path: Path
    width: float
    height: float
    bbox_area: float