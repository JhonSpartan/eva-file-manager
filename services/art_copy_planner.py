from pathlib import Path

from models.copy_models import (
    ArtSelection,
    SelectionState,
    CopyPlan,
    DestinationCopyPlan,
)


class ArtCopyPlanner:

    def _build_destination_plan(
            self,
            source: ArtSelection,
            destination: ArtSelection,
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

            id_name = source_id_path.name
            destination_id_path = destination_ids.get(id_name)

            source_files = source.files_by_id.get(
                source_id_path,
                [],
            )

            if destination_id_path is None:
                plan.ids_to_create.append(id_name)
                plan.files_to_copy.extend(source_files)
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

            plan.files_to_copy.extend(
                source_files
            )

        return plan

    def build(
            self,
            source: ArtSelection,
            destinations: list[ArtSelection],
    ) -> CopyPlan:

        plan = CopyPlan(
            source_art=source.art_path,
        )

        for destination in destinations:
            destination_plan = self._build_destination_plan(
                source,
                destination,
            )

            plan.destinations.append(destination_plan)

        return plan