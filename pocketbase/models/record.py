from __future__ import annotations

from typing import Any

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.utils import camel_to_snake


class Record(BaseModel):
    collection_id: str
    collection_name: str
    expand: dict[str, Any]

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.expand = {}
        for key, value in data.items():
            key = camel_to_snake(key).replace("@", "")
            setattr(self, key, value)
        self.load_expanded()

    @classmethod
    def parse_expanded(cls, data: Any):
        if isinstance(data, list):
            return [cls(a) for a in data]  # type: ignore
        return cls(data)

    def load_expanded(self) -> None:
        for key, value in self.expand.items():
            self.expand[key] = self.parse_expanded(value)
