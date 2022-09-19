from __future__ import annotations

from typing import Optional

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.utils.schema_field import SchemaField


class Collection(BaseModel):
    name: str
    schema: list[SchemaField]
    system: bool
    list_rule: Optional[str]
    view_rule: Optional[str]
    create_rule: Optional[str]
    update_rule: Optional[str]
    delete_rule: Optional[str]

    def load(self, data: dict) -> None:
        super().load(data)
        self.name = data.get("name", "")
        self.system = data.get("system", False)
        self.list_rule = data.get("listRule", None)
        self.view_rule = data.get("viewRule", None)
        self.create_rule = data.get("createRule", None)
        self.update_rule = data.get("updateRule", None)
        self.delete_rule = data.get("deleteRule", "")
        schema = data.get("schema", [])
        self.schema = []
        for field in schema:
            self.schema.append(SchemaField(**field))
