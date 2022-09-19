from __future__ import annotations

import re
import datetime
from typing import Union


def camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def to_datetime(
    str_datetime: str, format: str = "%Y-%m-%d %H:%M:%S"
) -> Union[datetime.datetime, str]:
    str_datetime = str_datetime.split(".")[0]
    try:
        return datetime.datetime.strptime(str_datetime, format)
    except Exception:
        return str_datetime
