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
    onCreate: bool = False
    onUpdate: bool = False
    onlyInt: bool = False
    exceptDomains: list[str] = field(default_factory=list)
    onlyDomains: list[str] = field(default_factory=list)
    maxSize: int | None = None
    cascadeDelete: bool = False
    collectionId: str | None = None
    maxSelect: int | None = None
    minSelect: int | None = None
    mimeTypes: list[str] = field(default_factory=list)
    protected: bool = False
    thumbs: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
