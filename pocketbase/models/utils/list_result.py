from __future__ import annotations

from dataclasses import dataclass, field

from pocketbase.models.utils.base_model import BaseModel


@dataclass
class ListResult:
    page: int = 1
    per_page: int = 0
    total_items: int = 0
    total_pages: int = 0
    items: list[BaseModel] = field(default_factory=list)
