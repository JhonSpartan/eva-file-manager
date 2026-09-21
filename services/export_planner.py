from pathlib import Path

from models.file_action_models import (
    ExportLevel,
    ExportOperation,
    ExportPlan,
)


class ExportPlanner:

    def build_plan(
            self,
            files: list[Path],
            level: ExportLevel,
            destination_root: Path,
    ) -> ExportPlan:

        plan = ExportPlan(
            level=level,
            destination_root=destination_root,
        )

        source_paths = self.get_source_paths(
            files=files,
            level=level,
        )

        planned_destinations: set[Path] = set()

        for source_path in source_paths:

            destination_path = (
                self.get_destination_path(
                    source_path=source_path,
                    level=level,
                    destination_root=destination_root,
                )
            )

            if destination_path.exists():
                plan.conflicts.append(
                    destination_path
                )
                continue

            if destination_path in planned_destinations:
                plan.conflicts.append(
                    destination_path
                )
                continue

            planned_destinations.add(
                destination_path
            )

            plan.operations.append(
                ExportOperation(
                    source_path=source_path,
                    destination_path=destination_path,
                )
            )

        return plan

    def get_source_paths(
            self,
            files: list[Path],
            level: ExportLevel,
    ) -> list[Path]:

        source_paths: set[Path] = set()

        for file_path in files:

            if level == ExportLevel.FILE:
                source_path = file_path

            elif level == ExportLevel.ART:
                source_path = file_path.parent.parent

            elif level == ExportLevel.EVA:
                source_path = file_path.parent.parent.parent

            else:
                continue

            source_paths.add(
                source_path
            )

        return sorted(
            source_paths
        )

    def get_destination_path(
            self,
            source_path: Path,
            level: ExportLevel,
            destination_root: Path,
    ) -> Path:

        if level not in (
                ExportLevel.FILE,
                ExportLevel.ART,
                ExportLevel.EVA,
        ):
            raise ValueError(
                f"Unsupported export level: {level}"
            )

        return destination_root / source_path.name

        raise ValueError(
            f"Unsupported export level: {level}"
        )