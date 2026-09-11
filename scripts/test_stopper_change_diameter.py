from pathlib import Path

from database.database import Database
from database.repositories.stopper_repository import (
    StopperRepository,
)
from services.stopper_detector import StopperDetector
from services.stopper_editor import StopperEditor
from services.stopper_validator import StopperValidator


def main() -> None:
    file_path = Path(
        r"D:\EVA5925_art-10372_2_driver_footrest_vlv.dxf"
    )

    stopper_name = "av"
    new_diameter = 6.0

    database = Database(
        Path.home() / ".eva" / "eva.db"
    )

    stopper_repository = StopperRepository(
        database
    )

    stopper = stopper_repository.get_by_name(
        stopper_name
    )

    if stopper is None:
        raise RuntimeError(
            f"Stopper not found: {stopper_name}"
        )

    detector = StopperDetector()
    validator = StopperValidator()

    editor = StopperEditor(
        detector=detector,
        validator=validator,
    )

    result = editor.change_diameter(
        file_path=file_path,
        expected_diameter=stopper.diameter,
        new_diameter=new_diameter,
    )

    print(
        "Changed stoppers:",
        result.changed_count,
    )


if __name__ == "__main__":
    main()