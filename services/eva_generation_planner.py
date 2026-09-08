from pathlib import Path

from models.eva_models import (
    PreparedEva,
    SessionTemplate,
    GenerationFile,
    GenerationPlan,
)

from services.copy_rules import (
    CopyRuleService,
)


class EvaGenerationPlanner:

    def __init__(
            self,
            copy_rule_service: CopyRuleService,
    ):
        self.copy_rule_service = (
            copy_rule_service
        )

    def build_plan(
            self,
            destination_root: Path,
            prepared_evas: list[PreparedEva],
            session_templates: list[SessionTemplate],
            five_d_mode: bool,
    ) -> GenerationPlan:

        plan = GenerationPlan(
            destination_root=destination_root
        )

        for prepared_eva in prepared_evas:
            for article in prepared_eva.articles:
                for template in session_templates:

                    if not template.selected:
                        continue

                    destination_folder_id = (
                        self.copy_rule_service
                        .resolve_template_folder_id(
                            template.folder_id,
                            five_d_mode,
                        )
                    )

                    filename = (
                        f"{prepared_eva.name}_"
                        f"{article}_"
                        f"{destination_folder_id}_"
                        f"{template.template_name}.dxf"
                    )

                    destination_file = (
                        destination_root
                        / prepared_eva.name
                        / article
                        / str(destination_folder_id)
                        / filename
                    )

                    plan.files.append(
                        GenerationFile(
                            eva_name=prepared_eva.name,
                            article=article,
                            destination_folder_id=destination_folder_id,
                            template_name=template.template_name,
                            destination_file=destination_file,
                            stopper_combination=template.stopper_combination,
                        )
                    )

        return plan