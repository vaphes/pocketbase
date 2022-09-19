from __future__ import annotations

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.utils import camel_to_snake


class Record(BaseModel):
    collection_id: str
    collection_name: str
    expand: dict

    def load(self, data: dict) -> None:
        super().load(data)
        for key, value in data.items():
            key = camel_to_snake(key).replace("@", "")
            setattr(self, key, value)
        self.collection_id = data.get("@collectionId", "")
        self.collection_name = data.get("@collectionName", "")
        expand = data.get("@expand", {})
        if expand:
            self.expand = expand
            self.load_expanded()

    @classmethod
    def parse_expanded(cls, data: dict):
        return cls(data)

    def load_expanded(self) -> None:
        for key, value in self.expand.items():
            self.expand[key] = self.parse_expanded(value)
