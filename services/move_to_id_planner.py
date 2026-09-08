from pathlib import Path

from models.file_action_models import (
    MoveFileOperation,
    MoveToIdPlan,
)


class MoveToIdPlanner:

    def build_plan(
            self,
            files: list[Path],
            destination_id: str,
    ) -> MoveToIdPlan:

        plan = MoveToIdPlan(
            destination_id=destination_id
        )

        planned_destinations: set[Path] = set()

        for source_file in files:

            source_id_path = source_file.parent

            if source_id_path.name == destination_id:
                continue

            destination_id_path = (
                source_id_path.parent
                / destination_id
            )

            destination_filename = (
                self.build_destination_filename(
                    source_file=source_file,
                    destination_id=destination_id,
                )
            )

            destination_file = (
                destination_id_path
                / destination_filename
            )

            if destination_file.exists():
                plan.conflicts.append(
                    destination_file
                )
                continue

            if destination_file in planned_destinations:
                plan.conflicts.append(
                    destination_file
                )
                continue

            planned_destinations.add(
                destination_file
            )

            plan.source_id_paths.add(
                source_id_path
            )

            plan.operations.append(
                MoveFileOperation(
                    source_file=source_file,
                    destination_file=destination_file,
                )
            )

        return plan

    def build_destination_filename(
            self,
            source_file: Path,
            destination_id: str,
    ) -> str:

        parts = source_file.stem.split(
            "_",
            3,
        )

        if len(parts) != 4:
            raise ValueError(
                (
                    "Неверный формат имени файла: "
                    f"{source_file.name}"
                )
            )

        eva_name = parts[0]
        article = parts[1]
        template_name = parts[3]

        new_stem = (
            f"{eva_name}_"
            f"{article}_"
            f"{destination_id}_"
            f"{template_name}"
        )

        return (
                new_stem
                + source_file.suffix
        )