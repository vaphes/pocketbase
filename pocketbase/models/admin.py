from __future__ import annotations

from typing import Union
import datetime

from pocketbase.utils import to_datetime
from pocketbase.models.utils.base_model import BaseModel


class Admin(BaseModel):
    avatar: int
    email: str
    last_reset_sent_at: Union[str, datetime.datetime]

    def load(self, data: dict) -> None:
        super().load(data)
        self.avatar = data.get("avatar", 0)
        self.email = data.get("email", "")
        self.last_reset_sent_at = to_datetime(data.get("lastResetSentAt", ""))
