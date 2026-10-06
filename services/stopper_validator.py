from models.stopper_candidate import StopperCandidate
from models.stopper_validation_result import StopperValidationResult


class StopperValidator:

    DXF_TO_MM = 10.0
    DIAMETER_TOLERANCE_MM = 0.5

    def validate(
            self,
            candidate: StopperCandidate,
            expected_diameter: float,
    ) -> StopperValidationResult:

        detected_width_mm = (
            candidate.width
            * self.DXF_TO_MM
        )

        detected_height_mm = (
            candidate.height
            * self.DXF_TO_MM
        )

        detected_diameter = (
                                    detected_width_mm
                                    + detected_height_mm
                            ) / 2

        difference = abs(
            detected_diameter
            - expected_diameter
        )

        width_difference = abs(
            detected_width_mm
            - expected_diameter
        )

        height_difference = abs(
            detected_height_mm
            - expected_diameter
        )

        is_valid = (
                width_difference
                <= self.DIAMETER_TOLERANCE_MM
                and
                height_difference
                <= self.DIAMETER_TOLERANCE_MM
        )

        return StopperValidationResult(
            is_valid=is_valid,
            detected_diameter=detected_diameter,
            expected_diameter=expected_diameter,
            difference=difference,
        )