from database.repositories.copy_rule_repository import CopyRuleRepository

class CopyRuleService:

    def __init__(
            self,
            repository: CopyRuleRepository,
    ):
        self.repository = repository

    def resolve_destination_id_name(
            self,
            source_id_name: str,
            mode: str | None,
    ) -> str:

        if mode is None:
            return source_id_name

        destination_id = self.repository.get_destination_id(
            mode,
            source_id_name,
        )

        return destination_id or source_id_name