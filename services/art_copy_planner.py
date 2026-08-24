from pathlib import Path

from models.copy_models import (
    ArtSelection,
    SelectionState,
    CopyPlan,
    DestinationCopyPlan, FileCopyOperation,
)
from services.copy_rules import CopyRuleService


class ArtCopyPlanner:

    def __init__(
            self,
            copy_rule_service: CopyRuleService,
    ):
        self.copy_rule_service = copy_rule_service

    def _add_copy_operations(
            self,
            plan: DestinationCopyPlan,
            source_files: list[Path],
            destination_id: Path,
    ):
        for source_file in source_files:
            plan.copy_operations.append(
                FileCopyOperation(
                    source_file=source_file,
                    destination_id=destination_id,
                )
            )

    def _build_destination_plan(
            self,
            source: ArtSelection,
            destination: ArtSelection,
            five_d_mode: bool,
    ) -> DestinationCopyPlan:

        plan = DestinationCopyPlan(
            destination_art=destination.art_path,
        )

        destination_ids = {
            id_path.name: id_path
            for id_path in destination.id_states
        }

        for source_id_path, source_state in source.id_states.items():

            if source_state == SelectionState.NONE:
                continue

            source_id_name = source_id_path.name

            mode = "5D" if five_d_mode else None

            destination_id_name = (
                self.copy_rule_service.resolve_destination_id_name(
                    source_id_name,
                    mode,
                )
            )

            destination_id_path = destination_ids.get(
                destination_id_name
            )

            source_files = source.files_by_id.get(
                source_id_path,
                [],
            )

            if destination_id_path is None:
                plan.ids_to_create.append(
                    destination_id_name
                )

                destination_id = (
                        destination.art_path
                        / destination_id_name
                )

                self._add_copy_operations(
                    plan,
                    source_files,
                    destination_id,
                )

                continue

            destination_state = destination.id_states[
                destination_id_path
            ]

            destination_files = destination.files_by_id.get(
                destination_id_path,
                [],
            )

            if destination_state != SelectionState.NONE:
                plan.files_to_delete.extend(
                    destination_files
                )

            self._add_copy_operations(
                plan,
                source_files,
                destination_id_path,
            )

        return plan

    def build(
            self,
            source: ArtSelection,
            destinations: list[ArtSelection],
            five_d_mode: bool = False,
    ) -> CopyPlan:

        plan = CopyPlan(
            source_art=source.art_path,
        )

        for destination in destinations:
            destination_plan = self._build_destination_plan(
                source,
                destination,
                five_d_mode,
            )

            plan.destinations.append(destination_plan)

        return plan