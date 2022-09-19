from __future__ import annotations

from typing import Optional, Union
import datetime

from pocketbase.utils import to_datetime
from pocketbase.models.record import Record
from pocketbase.models.utils.base_model import BaseModel


class User(BaseModel):
    email: str
    verified: bool
    last_reset_sent_at: Union[str, datetime.datetime]
    last_verification_sent_at: Union[str, datetime.datetime]
    profile: Optional[Record]

    def load(self, data: dict) -> None:
        super().load(data)
        self.email = data.get("email", "")
        self.verified = data.get("verified", "")
        self.last_reset_sent_at = to_datetime(data.get("lastResetSentAt", ""))
        self.last_verification_sent_at = to_datetime(
            data.get("lastVerificationSentAt", "")
        )
        profile = data.get("profile", None)
        self.profile = None
        if profile:
            self.profile = Record(profile)
