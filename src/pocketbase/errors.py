from __future__ import annotations

from typing import Any


class ClientResponseError(Exception):
    def __init__(
        self,
        *args: Any,
        url: str = "",
        status: int = 0,
        data: dict[str, Any] | None = None,
        is_abort: bool = False,
        original_error: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args)
        self.url = url
        self.status = status
        self.data = data or {}
        self.is_abort = is_abort
        self.original_error = original_error

    def __str__(self) -> str:
        base_message = super().__str__() or "ClientResponseError"
        details = [
            f"Message: {base_message}",
            f"URL: {self.url or 'N/A'}",
            f"Status: {self.status or 'N/A'}",
            f"Data: {self.data or 'N/A'}",
            f"Is Abort: {self.is_abort}",
            f"Original Error: {self.original_error or 'N/A'}",
        ]
        return "\n".join(details)
