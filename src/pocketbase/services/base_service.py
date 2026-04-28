from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pocketbase.client import Client


class BaseService(ABC):
    def __init__(self, client: Client) -> None:
        super().__init__()
        self.client = client
