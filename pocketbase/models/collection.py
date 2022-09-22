from __future__ import annotations

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.utils.schema_field import SchemaField


class Collection(BaseModel):
    name: str
    schema: list[SchemaField]
    system: bool
    list_rule: str | None
    view_rule: str | None
    create_rule: str | None
    update_rule: str | None
    delete_rule: str | None

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
