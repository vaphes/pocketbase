from __future__ import annotations

import datetime
from typing import Any

from pocketbase.models.utils import BaseModel
from pocketbase.utils import to_datetime


class Backup(BaseModel):
    key: str
    modified: str | datetime.datetime
    size: int

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.key = data.get("key", "")
        self.modified = to_datetime(data.pop("modified", ""))
        self.size = data.get("size", 0)
