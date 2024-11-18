from __future__ import annotations

import os
import pickle
from typing import Any

from pocketbase.models.admin import Admin
from pocketbase.models.record import Record
from pocketbase.stores.base_auth_store import BaseAuthStore


class LocalAuthStore(BaseAuthStore):
    filename: str
    filepath: str

    def __init__(
        self,
        filename: str = "pocketbase_auth.data",
        filepath: str = "",
        base_token: str = "",
        base_model: Record | Admin | None = None,
    ) -> None:
        super().__init__(base_token, base_model)
        self.filename = filename
        self.filepath = filepath
        self.complete_filepath = os.path.join(filepath, filename)

    @property
    def token(self) -> str:
        data = self._storage_get(self.complete_filepath)
        if not data or "token" not in data:
            return ""
        return data["token"]

    @property
    def model(self) -> Record | Admin | None:
        data = self._storage_get(self.complete_filepath)
        if not data or "model" not in data:
            return None
        return data["model"]

    def save(
        self, token: str = "", model: Record | Admin | None = None
    ) -> None:
        self._storage_set(
            self.complete_filepath, {"token": token, "model": model}
        )
        super().save(token, model)

    def clear(self) -> None:
        self._storage_remove(self.complete_filepath)
        super().clear()

    def _storage_set(self, key: str, value: Any) -> None:
        with open(key, "wb") as f:
            pickle.dump(value, f)

    def _storage_get(self, key: str) -> Any:
        try:
            with open(key, "rb") as f:
                value = pickle.load(f)
            return value
        except FileNotFoundError:
            return {}

    def _storage_remove(self, key: str) -> None:
        if os.path.exists(key):
            os.remove(key)
