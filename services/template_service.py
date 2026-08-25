from database.repositories.template_repository import TemplateRepository


class TemplateService:

    def __init__(
            self,
            repository: TemplateRepository,
    ):
        self.repository = repository

    def get_grouped_templates(self) -> dict[int, list[str]]:
        records = self.repository.get_all()

        grouped: dict[int, list[str]] = {}

        for record in records:
            grouped.setdefault(
                record.folder_id,
                []
            ).append(
                record.template_name
            )

        return grouped