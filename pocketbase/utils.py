from __future__ import annotations

import base64
import datetime
import json
import re

from .errors import ClientResponseError  # noqa: F401


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


def normalize_base64(encoded_str: str):
    encoded_str = encoded_str.strip()
    padding_needed = len(encoded_str) % 4
    if padding_needed:
        encoded_str += "=" * (4 - padding_needed)
    return encoded_str


def validate_token(token: str) -> bool:
    if len(token.split(".")) != 3:
        return False
    decoded_bytes = base64.urlsafe_b64decode(
        normalize_base64(token.split(".")[1])
    )
    decoded_str = decoded_bytes.decode("utf-8")
    data = json.loads(decoded_str)
    exp = data["exp"]
    if not isinstance(exp, int):
        try:
            exp = int(exp)
        except ValueError or TypeError:
            return False
    current_time = datetime.datetime.now().timestamp()
    return exp > current_time
