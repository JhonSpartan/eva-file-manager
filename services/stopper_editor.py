from pathlib import Path
import ezdxf
from ezdxf.math import Matrix44, Vec2
from ezdxf.path import make_path
from models.stopper_edit_result import StopperEditResult
from services.stopper_detector import StopperDetector
from services.stopper_validator import StopperValidator


class StopperEditor:
    DEFPOINTS_LAYER = "Defpoints"
    CENTER_TOLERANCE = 0.0001

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
            deleted_count=len(valid_candidates)
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


    def get_entity_center(
            self,
            entity,
    ) -> Vec2:
        path = make_path(
            entity
        )

        bbox = path.bbox()

        center_x = (
                           bbox.extmin.x
                           + bbox.extmax.x
                   ) / 2

        center_y = (
                           bbox.extmin.y
                           + bbox.extmax.y
                   ) / 2

        return Vec2(
            center_x,
            center_y,
        )

    def centers_are_equal(
            self,
            center_before: Vec2,
            center_after: Vec2,
    ) -> bool:
        distance = (
                center_before
                - center_after
        ).magnitude

        return (
                distance
                <= self.CENTER_TOLERANCE
        )

    def change_diameter(
            self,
            file_path: Path,
            expected_diameter: float,
            new_diameter: float,
    ) -> StopperEditResult:
        document = ezdxf.readfile(
            file_path
        )

        modelspace = document.modelspace()

        candidates = self.detector.find_candidates(
            modelspace
        )

        changed_count = 0

        for candidate in candidates:
            validation = self.validator.validate(
                candidate,
                expected_diameter,
            )

            if not validation.is_valid:
                continue

            current_diameter = (
                validation.detected_diameter
            )

            if current_diameter <= 0:
                continue

            scale_factor = (
                    new_diameter
                    / current_diameter
            )

            center_before = (
                self.get_entity_center(
                    candidate.entity
                )
            )

            transform = Matrix44.chain(
                Matrix44.translate(
                    -center_before.x,
                    -center_before.y,
                    0,
                ),
                Matrix44.scale(
                    scale_factor,
                    scale_factor,
                    1,
                ),
                Matrix44.translate(
                    center_before.x,
                    center_before.y,
                    0,
                ),
            )

            candidate.entity.transform(
                transform
            )

            center_after = (
                self.get_entity_center(
                    candidate.entity
                )
            )

            if not self.centers_are_equal(
                    center_before,
                    center_after,
            ):
                raise RuntimeError(
                    (
                        "Центр стопера сместился после "
                        f"масштабирования: {file_path}"
                    )
                )

            changed_count += 1

        if changed_count:
            self.finalize_document(
                document=document,
                file_path=file_path,
            )

        return StopperEditResult(
            changed_count=changed_count,
        )