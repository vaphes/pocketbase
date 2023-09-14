from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SchemaField:
    id: str = ""
    name: str = ""
    type: str = "text"
    system: bool = False
    required: bool = False
    presentable: bool = False
    unique: bool = False
    options: dict = field(default_factory=dict)
