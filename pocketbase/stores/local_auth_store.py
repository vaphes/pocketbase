from __future__ import annotations

from typing import Any, Optional, Union
import pickle
import os

from pocketbase.stores.base_auth_store import BaseAuthStore
from pocketbase.models.user import User
from pocketbase.models.admin import Admin


class LocalAuthStore(BaseAuthStore):
    filename: str
    filepath: str

    def __init__(
        self,
        filename: str = "pocketbase_auth.data",
        filepath: str = "",
        base_token: str = "",
        base_model: Optional[Union[User, Admin]] = None,
    ) -> None:
        super().__init__(base_token, base_model)
        self.filename = filename
        self.filepath = filepath
        self.complete_filepath = os.path.join(filepath, filename)

    @property
    def token(self) -> str:
        data = self._storage_get(self.complete_filepath)
        if not data or not "token" in data:
            return None
        return data["token"]

    @property
    def model(self) -> Union[User, Admin, None]:
        data = self._storage_get(self.complete_filepath)
        if not data or not "model" in data:
            return None
        return data["model"]

    def save(self, token: str = "", model: Optional[Union[User, Admin]] = None) -> None:
        self._storage_set(self.complete_filepath, {"token": token, "model": model})
        super().save(token, model)

    def clear(self) -> None:
        self._storage_remove(self.complete_filepath)
        super().clear()

    def _storage_set(self, key: str, value: Any) -> None:
        with open(key, "wb") as f:
            pickle.dump(value, f)

    def _storage_get(self, key: str) -> Any:
        with open(key, "rb") as f:
            value = pickle.load(f)
        return value

    def _storage_remove(self, key: str) -> None:
        if os.path.exists(key):
            os.remove(key)
