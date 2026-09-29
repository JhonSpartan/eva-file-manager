from pathlib import Path


def build_destination_file(
        source_file: Path,
        destination_id: Path,
) -> Path:
    name_parts = source_file.stem.split("_")

    destination_eva = destination_id.parent.parent.name
    destination_art = destination_id.parent.name
    destination_id_name = destination_id.name

    name_parts[0:1] = [destination_eva]
    name_parts[1:2] = [destination_art]
    name_parts[2:3] = [destination_id_name]

    return (
        destination_id
        / (
            "_".join(name_parts)
            + source_file.suffix.lower()
        )
    )