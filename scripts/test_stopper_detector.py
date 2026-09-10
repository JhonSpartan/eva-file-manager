import sys
from pathlib import Path

import ezdxf

from services.stopper_detector import StopperDetector
from services.stopper_validator import StopperValidator

from database.database import Database
from database.repositories.stopper_repository import (
    StopperRepository,
)


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:"
            " python -m scripts.test_stopper_detector"
            ' "path\\to\\file.dxf"'
        )
        return

    file_path = Path(
        sys.argv[1]
    )

    if not file_path.exists():
        print(
            "File not found:",
            file_path,
        )
        return

    document = ezdxf.readfile(
        file_path
    )

    detector = StopperDetector()
    validator = StopperValidator()

    database = Database(
        Path.home()
        / ".eva"
        / "eva.db"
    )
    stopper_repository = StopperRepository(
        database
    )

    candidates = detector.find_candidates(
        document.modelspace()
    )


    # Пока только для проверки StopperValidator.
    # Позже диаметр будет получаться из stopper_catalog.
    stopper_name = "fc"

    stopper = stopper_repository.get_by_name(
        stopper_name
    )

    if stopper is None:
        print(
            "Stopper not found:",
            stopper_name,
        )
        return

    expected_diameter = stopper.diameter

    print()
    print(
        "FILE:",
        file_path,
    )

    print(
        "STOPPER CANDIDATES:",
        len(candidates),
    )

    for candidate in candidates:
        result = validator.validate(
            candidate=candidate,
            expected_diameter=expected_diameter,
        )

        print()

        print(
            candidate.entity.dxftype(),
            "handle=",
            candidate.entity.dxf.handle,
        )

        print(
            "  width:",
            round(
                candidate.width,
                3,
            ),
        )

        print(
            "  height:",
            round(
                candidate.height,
                3,
            ),
        )

        print(
            "  detected:",
            round(
                result.detected_diameter,
                3,
            ),
            "mm",
        )

        print(
            "  expected:",
            result.expected_diameter,
            "mm",
        )

        print(
            "  difference:",
            round(
                result.difference,
                3,
            ),
            "mm",
        )

        print(
            "  valid:",
            result.is_valid,
        )


if __name__ == "__main__":
    main()