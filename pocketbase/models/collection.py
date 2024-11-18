from __future__ import annotations

from typing import Any

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.utils.schema_field import SchemaField


class Collection(BaseModel):
    name: str
    type: str
    schema: list[SchemaField]
    system: bool
    list_rule: str | None
    view_rule: str | None
    create_rule: str | None
    update_rule: str | None
    delete_rule: str | None
    options: dict[str, Any]

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.name = data.get("name", "")
        self.system = data.get("system", False)
        self.type = data.get("type", "base")
        self.options = data.get("options", {})

        # rules
        self.list_rule = data.get("listRule", None)
        self.view_rule = data.get("viewRule", None)
        self.create_rule = data.get("createRule", None)
        self.update_rule = data.get("updateRule", None)
        self.delete_rule = data.get("deleteRule", "")

        # schema
        schema = data.get("schema", [])
        self.schema = []
        for field in schema:
            self.schema.append(SchemaField(**field))

    def is_base(self):
        return self.type == "base"

    def is_auth(self):
        return self.type == "auth"

    def is_single(self):
        return self.type == "single"
