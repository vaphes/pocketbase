from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from typing import Protocol

from pocketbase.models.record import Record
from pocketbase.utils import get_token_payload, is_token_expired

OnStoreChangeCallback = Callable[[str, Record | None], None]


class AuthStoreProtocol(Protocol):
    @property
    def token(self) -> str: ...

    @property
    def model(self) -> Record | None: ...

    def save(self, token: str = "", model: Record | None = None) -> None: ...

    def clear(self) -> None: ...


class BaseAuthStore(ABC):
    """
    Base AuthStore class that is intended to be extended by all other
    PocketBase AuthStore implementations.
    """

    def __init__(
        self, base_token: str = "", base_model: Record | None = None
    ) -> None:
        super().__init__()
        self.base_token = base_token
        self.base_model = base_model
        self._on_change_callbacks: list[OnStoreChangeCallback] = []

    @property
    def token(self) -> str:
        """Retrieves the stored token (if any)."""
        return self.base_token

    @property
    def record(self) -> Record | None:
        """Retrieves the stored model data (if any)."""
        return self.base_model

    @property
    def model(self) -> Record | None:
        """Retrieves the stored model data (if any)."""
        return self.base_model

    @property
    def is_valid(self) -> bool:
        """Checks if the auth store has a valid token."""
        return not is_token_expired(self.token)

    @property
    def is_superuser(self) -> bool:
        """Checks if the stored model data has superuser privileges."""
        payload = get_token_payload(self.token)
        type_ = payload.get("type")
        collection_name = payload.get("collection_name")
        collection_id = payload.get("collection_id")
        return type_ == "auth" and (
            collection_name == "_superusers"
            or (not collection_name and collection_id == "pbc_3142635823")
        )

    def save(self, token: str = "", model: Record | None = None) -> None:
        """Saves the provided new token and model data in the auth store."""

        self.base_token = token if token else ""
        self.base_model = model if model else None
        self._trigger_on_change()

    def clear(self) -> None:
        """Removes the stored token and model data form the auth store."""
        self.base_token = ""
        self.base_model = None
        self._trigger_on_change()

    def on_change(
        self,
        callback: OnStoreChangeCallback,
        fire_immediately: bool = False,
    ) -> Callable[[], None]:
        """Register a callback function that will be called on store change.

        You can set the `fire_immediately` argument to true in order to invoke
        the provided callback right after registration.

        Returns a removal function that you could call to "unsubscribe" from
        the changes.
        """
        # This method can be implemented in child classes to support change listeners.
        self._on_change_callbacks.append(callback)
        if fire_immediately:
            callback(self.token, self.record)
        return lambda: self._unsubscribe_on_change(callback)

    def _unsubscribe_on_change(self, callback: OnStoreChangeCallback) -> None:
        """Unregisters a previously registered callback function."""
        if callback in self._on_change_callbacks:
            self._on_change_callbacks.remove(callback)

    def _trigger_on_change(self) -> None:
        """Triggers all registered on_change callbacks."""
        for callback in self._on_change_callbacks:
            callback(self.token, self.record)
