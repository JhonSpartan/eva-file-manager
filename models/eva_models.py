from dataclasses import dataclass


@dataclass
class PreparedEva:
    name: str
    articles: list[str]