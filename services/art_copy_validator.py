from pathlib import Path

from models.copy_models import (
    ArtSelection,
    SelectionState,
    CopyValidationIssue,
    CopyValidationResult,
    ValidationIssueType, ValidationAction,
)


class ArtCopyValidator:
    def validate(
            self,
            source: ArtSelection | None,
            destinations: list[ArtSelection],
    ) -> CopyValidationResult:

        result = CopyValidationResult()

        if source is None:
            result.issues.append(
                CopyValidationIssue(
                    issue_type=ValidationIssueType.NO_SOURCE_ART,
                    action=ValidationAction.BLOCK,
                    message=(
                        "No source ART selected. "
                        "Select one source ART."
                    ),
                )
            )

        if not destinations:
            result.issues.append(
                CopyValidationIssue(
                    issue_type=ValidationIssueType.NO_DESTINATION_ARTS,
                    action=ValidationAction.BLOCK,
                    message=(
                        "No destination ART selected. "
                        "Select at least one destination ART."
                    ),
                )
            )

        if result.blocking_issues:
            return result

        for destination in destinations:
            self._validate_destination(
                source,
                destination,
                result,
            )

        return result

    def _validate_destination(
            self,
            source: ArtSelection,
            destination: ArtSelection,
            result: CopyValidationResult,
    ):
        destination_ids = {
            id_path.name: id_path
            for id_path in destination.id_states
        }

        for source_id_path, source_state in source.id_states.items():

            if source_state == SelectionState.NONE:
                continue

            id_name = source_id_path.name

            destination_id_path = destination_ids.get(id_name)

            if destination_id_path is None:
                self._add_missing_id_issue(
                    destination,
                    id_name,
                    result,
                )
                continue

            destination_state = destination.id_states[
                destination_id_path
            ]

            self._validate_existing_id(
                source=source,
                source_id_path=source_id_path,
                source_state=source_state,
                destination=destination,
                destination_id_path=destination_id_path,
                destination_state=destination_state,
                result=result,
            )

    def _add_missing_id_issue(
            self,
            destination: ArtSelection,
            id_name: str,
            result: CopyValidationResult,
    ):
        result.issues.append(
            CopyValidationIssue(
                issue_type=ValidationIssueType.MISSING_DESTINATION_ID,
                destination_art=destination.art_path,
                action=ValidationAction.CREATE_ID,
                id_name=id_name,
                message=(
                    f'ID "{id_name}" does not exist in '
                    f'"{destination.art_path.name}".'
                ),
            )
        )

    def _validate_existing_id(
            self,
            source: ArtSelection,
            source_id_path: Path,
            source_state: SelectionState,
            destination: ArtSelection,
            destination_id_path: Path,
            destination_state: SelectionState,
            result: CopyValidationResult,
    ):
        if (
                source_state == SelectionState.FULL
                and destination_state == SelectionState.NONE
        ):
            result.issues.append(
                CopyValidationIssue(
                    issue_type=ValidationIssueType.DESTINATION_ID_NOT_SELECTED,
                    action=ValidationAction.BLOCK,
                    destination_art=destination.art_path,
                    id_name=source_id_path.name,
                    message=(
                        f'ID "{source_id_path.name}" already exists in '
                        f'"{destination.art_path.name}", '
                        f"but it is not selected for replacement."
                    ),
                )
            )
            return

        if (
                source_state == SelectionState.PARTIAL
                and destination_state == SelectionState.NONE
        ):
            result.issues.append(
                CopyValidationIssue(
                    issue_type=ValidationIssueType.ADD_FILES_WITHOUT_REPLACEMENT,
                    action=ValidationAction.CONFIRM,
                    destination_art=destination.art_path,
                    id_name=source_id_path.name,
                    message=(
                        f'No files are selected for replacement in '
                        f'ID "{source_id_path.name}" of '
                        f'"{destination.art_path.name}".'
                    ),
                )
            )
            return