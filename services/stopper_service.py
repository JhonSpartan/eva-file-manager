from database.repositories.stopper_repository import StopperRepository


class StopperService:

    def __init__(
            self,
            repository: StopperRepository,
    ):
        self.repository = repository

    def get_grouped_stoppers(self) -> dict[int, list[str]]:
        records = self.repository.get_all()

        grouped: dict[int, list[str]] = {}

        for record in records:
            grouped.setdefault(
                record.diameter,
                []
            ).append(
                record.stopper_name
            )

        return grouped