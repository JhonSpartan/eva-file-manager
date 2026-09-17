from database.repositories.template_repository import TemplateRepository
from models.eva_models import StopperCombination, SessionTemplate, TemplateOrigin


class TemplateService:

    DRIVER_FOLDER_PAIRS = {
        1: 5,
        5: 1,
        2: 6,
        6: 2,
    }

    FIVE_D_DISABLED_FOLDER_IDS = {
        1,
        5,
    }

    def __init__(
            self,
            repository: TemplateRepository,
    ):
        self.repository = repository

    def get_session_templates(
            self,
    ) -> list[SessionTemplate]:
        records = self.repository.get_all()

        return [
            SessionTemplate(
                folder_id=record.folder_id,
                template_name=record.template_name,
                origin=TemplateOrigin.DATABASE,
                has_stoppers=record.has_stoppers,
            )
            for record in records
        ]

    def add_stopper_templates(
            self,
            templates: list[SessionTemplate],
            combinations: list[StopperCombination],
    ) -> list[SessionTemplate]:

        result = templates.copy()

        existing_names = {
            (
                template.folder_id,
                template.template_name,
            )
            for template in result
        }

        for template in templates:
            if template.origin != TemplateOrigin.DATABASE:
                continue

            if not template.has_stoppers:
                continue

            for combination in combinations:
                new_name = (
                    f"{template.template_name}_"
                    f"{combination.name}"
                )

                target_folder_ids = (
                    self.get_target_folder_ids(
                        template.folder_id,
                        new_name,
                    )
                )

                for folder_id in target_folder_ids:
                    key = (
                        folder_id,
                        new_name,
                    )

                    if key in existing_names:
                        continue

                    result.append(
                        SessionTemplate(
                            folder_id=folder_id,
                            template_name=new_name,
                            origin=TemplateOrigin.STOPPER,
                            selected=False,
                            stopper_combination=combination,
                        )
                    )

                    existing_names.add(key)

        return result

    def get_target_folder_ids(
            self,
            folder_id: int,
            template_name: str,
    ) -> list[int]:

        folder_ids = [folder_id]

        name_parts = (
            template_name
            .lower()
            .split("_")
        )

        is_driver_template = (
                "driver" in name_parts
        )

        is_passenger_template = (
                "passenger" in name_parts
        )

        if is_driver_template:
            paired_folder_id = (
                self.DRIVER_FOLDER_PAIRS.get(
                    folder_id
                )
            )

            if paired_folder_id is not None:
                folder_ids.append(
                    paired_folder_id
                )

        elif is_passenger_template:
            if folder_id == 1:
                folder_ids.append(2)

            elif folder_id == 2:
                folder_ids.append(1)

        return folder_ids

    def add_custom_templates(
            self,
            templates: list[SessionTemplate],
            custom_templates: list[SessionTemplate],
    ) -> list[SessionTemplate]:

        result = templates.copy()

        existing_names = {
            (
                template.folder_id,
                template.template_name,
            )
            for template in result
        }

        for template in custom_templates:

            target_folder_ids = (
                self.get_target_folder_ids(
                    template.folder_id,
                    template.template_name,
                )
            )

            for folder_id in target_folder_ids:
                key = (
                    folder_id,
                    template.template_name,
                )

                if key in existing_names:
                    continue

                result.append(
                    SessionTemplate(
                        folder_id=folder_id,
                        template_name=template.template_name,
                        origin=TemplateOrigin.CUSTOM,
                        selected=True,
                        stopper_combination=(
                            template.stopper_combination
                        ),
                    )
                )

                existing_names.add(key)

        return result

    def set_template_selected(
            self,
            templates: list[SessionTemplate],
            folder_id: int,
            template_name: str,
            selected: bool,
            five_d_mode: bool = False,
    ):
        target_folder_ids = (
            self.get_target_folder_ids(
                folder_id,
                template_name,
            )
        )

        if five_d_mode:
            target_folder_ids = [
                target_folder_id
                for target_folder_id in target_folder_ids
                if target_folder_id
                   not in self.FIVE_D_DISABLED_FOLDER_IDS
            ]

        for template in templates:
            if (
                    template.folder_id in target_folder_ids
                    and template.template_name == template_name
            ):
                template.selected = selected

