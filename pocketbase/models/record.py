from __future__ import annotations

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.utils import camel_to_snake
from dataclasses import dataclass, field

@dataclass
class Record(BaseModel):
    collection_id: str
    collection_name: str = ""
    expand: dict = field(default_factory=dict)

    def load(self, data: dict) -> None:
        super().load(data)
        self.expand = {}
        for key, value in data.items():
            key = camel_to_snake(key).replace("@", "")
            setattr(self, key, value)
        self.load_expanded()

    @classmethod
    def parse_expanded(cls, data: dict):
        return cls(data)

    def load_expanded(self) -> None:
        for key, value in self.expand.items():
            self.expand[key] = self.parse_expanded(value)
