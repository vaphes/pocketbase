from __future__ import annotations

from typing import Callable
import dataclasses
import asyncio

import httpx


@dataclasses.dataclass
class Event:
    """Representation of an event"""

    id: str = ""
    event: str = "message"
    data: str = ""
    retry: int | None = None


class SSEClient:
    """Implementation of a server side event client"""

    FIELD_SEPARATOR = ":"
    _listeners: dict = {}
    _loop_running: bool = False

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
        self.client = httpx.AsyncClient()

    async def _read(self):
        """Read the incoming event source stream and yield event chunks"""
        data = b""
        async with self.client.stream(
            self.method, self.url, headers=self.headers, data=self.payload, timeout=None
        ) as r:
            async for chunk in r.aiter_bytes():
                for line in chunk.splitlines(True):
                    data += line
                    if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                        yield data
                        data = b""
            if data:
                yield data

    async def _events(self):
        async for chunk in self._read():
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

    async def _loop(self):
        self._loop_running = True
        async for event in self._events():
            if event.event in self._listeners:
                self._listeners[event.event](event)

    def add_event_listener(self, event: str, callback: Callable[[Event], None]) -> None:
        self._listeners[event] = callback
        if not self._loop_running:
            asyncio.run(self._loop())

    def remove_event_listener(
        self, event: str, callback: Callable[[Event], None]
    ) -> None:
        if event in self._listeners:
            self._listeners.pop(event)

    def close(self) -> None:
        pass
