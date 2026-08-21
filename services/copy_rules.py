def resolve_destination_id_name(
        source_id_name: str,
        five_d_mode: bool,
) -> str:

    if five_d_mode and source_id_name == "8":
        return "7"

    return source_id_name