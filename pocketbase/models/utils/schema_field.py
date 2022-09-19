from dataclasses import dataclass, field
from typing import Any


@dataclass
class SchemaField:
    id: str = ""
    name: str = ""
    type: str = "text"
    system: bool = False
    required: bool = False
    unique: bool = False
    options: dict[str:Any] = field(default_factory=dict)
