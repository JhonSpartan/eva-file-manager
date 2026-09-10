from pathlib import Path

import ezdxf

from models.stopper_edit_result import StopperEditResult
from services.stopper_detector import StopperDetector
from services.stopper_validator import StopperValidator


class StopperEditor:
    DEFPOINTS_LAYER = "Defpoints"

    def __init__(
            self,
            detector: StopperDetector,
            validator: StopperValidator,
    ):
        self.detector = detector
        self.validator = validator

    def delete_stoppers(
            self,
            file_path: Path,
            expected_diameter: float,
    ) -> StopperEditResult:
        document = ezdxf.readfile(
            file_path
        )

        modelspace = document.modelspace()

        candidates = self.detector.find_candidates(
            modelspace
        )

        valid_candidates = []

        for candidate in candidates:
            validation = self.validator.validate(
                candidate,
                expected_diameter,
            )

            if validation.is_valid:
                valid_candidates.append(
                    candidate
                )

        for candidate in valid_candidates:
            modelspace.delete_entity(
                candidate.entity
            )

        if valid_candidates:
            self.finalize_document(
                document=document,
                file_path=file_path,
            )

        return StopperEditResult(
            deleted_count=len(
                valid_candidates
            ),
        )

    def finalize_document(
            self,
            document,
            file_path: Path,
    ) -> None:
        self.remove_defpoints_layer(
            document
        )

        self.save_document(
            document=document,
            file_path=file_path,
        )

    def remove_defpoints_layer(
            self,
            document,
    ) -> None:
        if self.DEFPOINTS_LAYER not in document.layers:
            return

        document.layers.remove(
            self.DEFPOINTS_LAYER
        )

    def save_document(
            self,
            document,
            file_path: Path,
    ) -> None:
        document.saveas(
            file_path
        )