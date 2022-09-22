from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass
class Event:
    """Representation of an event"""

    id: str = ""
    event: str = "message"
    data: str = ""
    retry: int | None = None


class SSEClient:
    """Implementation of a server side event client"""

    FIELD_SEPARATOR = ":"

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict | None = None,
        payload: dict | None = None,
        encoding="utf-8",
    ) -> None:
        self.url = url
        self.method = method
        self.headers = headers
        self.payload = payload
        self.encoding = encoding

    def _read(self):
        """Read the incoming event source stream and yield event chunks"""
        data = b""
        with httpx.stream(
            self.method, self.url, headers=self.headers, data=self.payload, timeout=None
        ) as r:
            for chunk in r.iter_bytes():
                for line in chunk.splitlines(True):
                    data += line
                    if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                        yield data
                        data = b""
            if data:
                yield data

    def events(self):
        for chunk in self._read():
            event = Event()
            for line in chunk.splitlines():
                line = line.decode(self.encoding)
                if not line.strip() or line.startswith(self.FIELD_SEPARATOR):
                    continue
                data = line.split(self.FIELD_SEPARATOR, 1)
                field = data[0]
                if field not in event.__dict__:
                    continue
                if len(data) > 1:
                    if data[1].startswith(" "):
                        value = data[1][1:]
                    else:
                        value = data[1]
                else:
                    value = ""
                if field == "data":
                    event.data += value + "\n"
                else:
                    setattr(event, field, value)
            if not event.data:
                continue
            if event.data.endswith("\n"):
                event.data = event.data[0:-1]
            event.event = event.event or "message"
            yield event
