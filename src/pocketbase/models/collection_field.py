from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CollectionField:
    id: str = ""
    name: str = ""
    type: str = "text"
    system: bool = False
    required: bool = False
    presentable: bool = False
    unique: bool = False
    options: dict[str, Any] = field(default_factory=dict)
    hidden: bool = False
    max: int | None = None
    min: int | None = None
    pattern: str | None = None
    primary_key: bool = False
    auto_generate_pattern: str | None = None
