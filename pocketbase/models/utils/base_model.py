from abc import ABC
from typing import Any, Union
import datetime

from pocketbase.utils import to_datetime


class BaseModel(ABC):
    id: str
    created: Union[str, datetime.datetime]
    updated: Union[str, datetime.datetime]

    def __init__(self, data: dict[str:Any] = {}) -> None:
        super().__init__()
        self.load(data)

    def load(self, data: dict[str:Any]) -> None:
        """Loads `data` into the current model."""
        self.id = data.pop("id", "")
        self.created = to_datetime(data.pop("created", ""))
        self.updated = to_datetime(data.pop("updated", ""))

    @property
    def is_new(self) -> bool:
        """Returns whether the current loaded data represent a stored db record."""
        return not self.id or self.id == "00000000-0000-0000-0000-000000000000"
