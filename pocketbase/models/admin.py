from __future__ import annotations

from typing import Any

from pocketbase.models.utils.base_model import BaseModel


class Admin(BaseModel):
    avatar: int
    email: str

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.avatar = data.get("avatar", 0)
        self.email = data.get("email", "")
