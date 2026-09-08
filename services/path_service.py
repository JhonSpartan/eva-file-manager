from pathlib import Path

from database.repositories.path_repository import (
    PathRepository,
)


class PathService:
    EVA_DEFAULT_OUTPUT_KEY = "eva_default_output"
    EVA_LAST_OUTPUT_KEY = "eva_last_output"

    FILES_DEFAULT_OUTPUT_KEY = "files_default_output"
    FILES_LAST_OUTPUT_KEY = "files_last_output"

    def __init__(
            self,
            repository: PathRepository,
    ):
        self.repository = repository

    def get_eva_default_output_path(
            self,
    ) -> Path | None:
        record = self.repository.get_by_key(
            self.EVA_DEFAULT_OUTPUT_KEY
        )

        if record is None:
            return None

        return record.path

    def set_eva_default_output_path(
            self,
            path: Path,
    ) -> None:
        self.repository.save(
            self.EVA_DEFAULT_OUTPUT_KEY,
            path,
        )

    def get_eva_last_output_path(
            self,
    ) -> Path | None:
        record = self.repository.get_by_key(
            self.EVA_LAST_OUTPUT_KEY
        )

        if record is None:
            return None

        return record.path

    def set_eva_last_output_path(
            self,
            path: Path,
    ) -> None:
        self.repository.save(
            self.EVA_LAST_OUTPUT_KEY,
            path,
        )

    def get_files_default_output_path(
            self,
    ) -> Path | None:

        record = self.repository.get_by_key(
            self.FILES_DEFAULT_OUTPUT_KEY
        )

        if record is None:
            return None

        return record.path

    def set_files_default_output_path(
            self,
            path: Path | None,
    ) -> None:

        self.repository.save(
            self.FILES_DEFAULT_OUTPUT_KEY,
            path,
        )

    def get_files_last_output_path(
            self,
    ) -> Path | None:

        record = self.repository.get_by_key(
            self.FILES_LAST_OUTPUT_KEY
        )

        if record is None:
            return None

        return record.path

    def set_files_last_output_path(
            self,
            path: Path | None,
    ) -> None:

        self.repository.save(
            self.FILES_LAST_OUTPUT_KEY,
            path,
        )



