from dataclasses import dataclass


@dataclass
class StopperValidationResult:
    is_valid: bool
    detected_diameter: float
    expected_diameter: float
    difference: float