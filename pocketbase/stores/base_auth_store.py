from __future__ import annotations

from abc import ABC
from typing import Protocol

from pocketbase.models.admin import Admin
from pocketbase.models.record import Record


class AuthStore(Protocol):
    @property
    def token(self) -> str: ...

    @property
    def model(self) -> Record | Admin | None: ...

    def save(
        self, token: str = "", model: Record | Admin | None = None
    ) -> None: ...

    def clear(self) -> None: ...


class BaseAuthStore(ABC):
    """
    Base AuthStore class that is intended to be extended by all other
    PocketBase AuthStore implementations.
    """

    base_token: str
    base_model: Record | Admin | None

    def __init__(
        self, base_token: str = "", base_model: Record | Admin | None = None
    ) -> None:
        super().__init__()
        self.base_token = base_token
        self.base_model = base_model

    @property
    def token(self) -> str:
        """Retrieves the stored token (if any)."""
        return self.base_token

    @property
    def model(self) -> Record | Admin | None:
        """Retrieves the stored model data (if any)."""
        return self.base_model

    def save(
        self, token: str = "", model: Record | Admin | None = None
    ) -> None:
        """Saves the provided new token and model data in the auth store."""

        self.base_token = token if token else ""
        self.base_model = model if model else None

    def clear(self) -> None:
        """Removes the stored token and model data form the auth store."""
        self.base_token = ""
        self.base_model = None
