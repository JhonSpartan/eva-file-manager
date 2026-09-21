from pathlib import Path

from models.copy_models import (
    ArtSelection,
    SelectionState,
    CopyValidationIssue,
    CopyValidationResult,
    ValidationIssueType,
    ValidationAction,
)
from services.copy_rules import CopyRuleService


class ArtCopyValidator:

    def __init__(
            self,
            copy_rule_service: CopyRuleService,
    ):
        self.copy_rule_service = copy_rule_service

    def validate(
            self,
            source: ArtSelection | None,
            destinations: list[ArtSelection],
            five_d_mode: bool = False,
    ) -> CopyValidationResult:

        result = CopyValidationResult()

        if source is None:
            result.issues.append(
                CopyValidationIssue(
                    issue_type=ValidationIssueType.NO_SOURCE_ART,
                    action=ValidationAction.BLOCK,
                    message=(
                        "Исходный ART не выбран. "
                        "Выберите один исходный ART."
                    ),
                )
            )

        if not destinations:
            result.issues.append(
                CopyValidationIssue(
                    issue_type=ValidationIssueType.NO_DESTINATION_ARTS,
                    action=ValidationAction.BLOCK,
                    message=(
                        "Целевые ART не выбраны. "
                        "Выберите хотя бы один целевой ART."
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
                five_d_mode,
            )

        self._adjust_destination_selection_issues(
            destinations,
            result,
        )

        return result

    def _adjust_destination_selection_issues(
            self,
            destinations: list[ArtSelection],
            result: CopyValidationResult,
    ) -> None:

        selected_id_names = set()

        for destination in destinations:
            for id_path, state in destination.id_states.items():

                if state == SelectionState.NONE:
                    continue

                selected_id_names.add(
                    id_path.name
                )

        for issue in result.issues:

            if (
                    issue.issue_type
                    != ValidationIssueType.DESTINATION_ID_NOT_SELECTED
            ):
                continue

            if issue.id_name not in selected_id_names:
                continue

            issue.action = ValidationAction.CONFIRM

    def _validate_destination(
            self,
            source: ArtSelection,
            destination: ArtSelection,
            result: CopyValidationResult,
            five_d_mode: bool,
    ):
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

            if destination_id_path is None:
                self._add_missing_id_issue(
                    destination,
                    destination_id_name,
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
        if destination.art_state != SelectionState.FULL:
            return

        result.issues.append(
            CopyValidationIssue(
                issue_type=ValidationIssueType.MISSING_DESTINATION_ID,
                destination_art=destination.art_path,
                action=ValidationAction.CREATE_ID,
                id_name=id_name,
                message=(
                    f'ID "{id_name}" отсутствует в '
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
                    id_name=destination_id_path.name,
                    message=(
                        f'ID "{destination_id_path.name}" уже существует в '
                        f'"{destination.art_path.name}", '
                        f"но не выбран для замены."
                    )
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
                    id_name=destination_id_path.name,
                    message=(
                        f'В ID "{destination_id_path.name}" артикула '
                        f'"{destination.art_path.name}" '
                        f"не выбраны файлы для замены."
                    )
                )
            )
            return