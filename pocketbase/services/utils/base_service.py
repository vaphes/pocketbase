from __future__ import annotations

from abc import ABC
import pocketbase.client as client


class BaseService(ABC):
    def __init__(self, client: client.Client) -> None:
        super().__init__()
        self.client: client.Client = client
