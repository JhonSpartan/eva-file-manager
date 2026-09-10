from pathlib import Path

from database.database import Database
from database.repositories.stopper_repository import (
    StopperRepository,
)
from services.stopper_detector import StopperDetector
from services.stopper_editor import StopperEditor
from services.stopper_validator import StopperValidator


def main() -> None:
    # Используем КОПИЮ тестового DXF
    file_path = Path(
        r"C:\ESD\EVA1087_art-729-1_2_driver_footrest_fc.dxf"
    )

    stopper_name = "av"

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

    result = editor.delete_stoppers(
        file_path=file_path,
        expected_diameter=stopper.diameter,
    )

    print(
        "Deleted stoppers:",
        result.deleted_count,
    )


if __name__ == "__main__":
    main()