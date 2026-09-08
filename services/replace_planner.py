from pathlib import Path

from models.file_action_models import (
    ReplaceMode,
    ReplaceOperation,
    ReplacePlan,
)


class ReplacePlanner:

    def build_plan(
            self,
            files: list[Path],
            find_text: str,
            replace_text: str,
            mode: ReplaceMode,
    ) -> ReplacePlan:

        plan = ReplacePlan(
            find_text=find_text,
            replace_text=replace_text,
            mode=mode,
        )

        for source_file in files:

            new_stem = source_file.stem.replace(
                find_text,
                replace_text,
            )

            if new_stem == source_file.stem:
                continue

            destination_file = (
                source_file.with_name(
                    new_stem + source_file.suffix
                )
            )

            if (
                    destination_file.exists()
                    and destination_file != source_file
            ):
                plan.conflicts.append(
                    destination_file
                )
                continue

            plan.operations.append(
                ReplaceOperation(
                    source_file=source_file,
                    destination_file=destination_file,
                )
            )

        return plan