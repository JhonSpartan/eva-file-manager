from pathlib import Path

from models.file_action_models import (
    DeleteLevel,
    DeleteOperation,
    DeletePlan,
)


class DeletePlanner:

    def build_plan(
            self,
            files: list[Path],
            level: DeleteLevel,
    ) -> DeletePlan:

        plan = DeletePlan(
            level=level
        )

        target_paths = self.get_target_paths(
            files=files,
            level=level,
        )

        for target_path in target_paths:

            if not target_path.exists():
                continue

            plan.operations.append(
                DeleteOperation(
                    target_path=target_path
                )
            )

        return plan

    def get_target_paths(
            self,
            files: list[Path],
            level: DeleteLevel,
    ) -> list[Path]:

        target_paths: set[Path] = set()

        for file_path in files:

            if level == DeleteLevel.FILE:
                target_path = file_path

            elif level == DeleteLevel.ID:
                target_path = file_path.parent

            elif level == DeleteLevel.ART:
                target_path = file_path.parent.parent

            elif level == DeleteLevel.EVA:
                target_path = file_path.parent.parent.parent

            else:
                raise ValueError(
                    f"Unsupported delete level: {level}"
                )

            target_paths.add(
                target_path
            )

        return sorted(
            target_paths
        )