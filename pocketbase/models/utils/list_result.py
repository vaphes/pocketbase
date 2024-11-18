from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from pocketbase.models.utils.base_model import Model

T = TypeVar("T", bound=Model)


@dataclass
class ListResult(Generic[T]):
    page: int = 1
    per_page: int = 0
    total_items: int = 0
    total_pages: int = 0
    items: list[T] = field(default_factory=list)
