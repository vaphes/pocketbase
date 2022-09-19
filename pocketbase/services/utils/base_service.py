from __future__ import annotations

from abc import ABC


class BaseService(ABC):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
