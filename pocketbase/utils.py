from __future__ import annotations

import re
import datetime
from typing import Any


def camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def to_datetime(
    str_datetime: str, format: str = "%Y-%m-%d %H:%M:%S"
) -> datetime.datetime | str:
    str_datetime = str_datetime.split(".")[0]
    try:
        return datetime.datetime.strptime(str_datetime, format)
    except Exception:
        return str_datetime


class ClientResponseError(Exception):
    url: str = ""
    status: int = 0
    data: dict = {}
    is_abort: bool = False
    original_error: Any | None = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)
        self.url = kwargs.get("url", "")
        self.status = kwargs.get("status", 0)
        self.data = kwargs.get("data", {})
        self.is_abort = kwargs.get("is_abort", False)
        self.original_error = kwargs.get("original_error", None)
