from pathlib import Path


def resource_path(*parts: str) -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "resources"
        / Path(*parts)
    )