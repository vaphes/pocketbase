from __future__ import annotations

from typing import Any

from pocketbase.models.utils.base_model import BaseModel


class ExternalAuth(BaseModel):
    record_id: str
    collection_id: str
    provider: str
    provider_id: str

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.record_id = data.get("recordId", "")
        self.collection_id = data.get("collectionId", "")
        self.provider = data.get("provider", "")
        self.provider_id = data.get("providerId", "")
