from __future__ import annotations

import dataclasses
import threading
from collections.abc import Callable
from typing import Any

import httpx


@dataclasses.dataclass
class Event:
    """Representation of an event"""

    id: str = ""
    event: str = "message"
    data: str = ""
    retry: int | None = None


class EventLoop(threading.Thread):
    FIELD_SEPARATOR = ":"

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        encoding: str = "utf-8",
        listeners: dict[str, Callable[[Event], Any]] | None = None,
        **kwargs: Any,
    ):
        threading.Thread.__init__(self, **kwargs)
        self.kill = False
        self.client = httpx.Client()
        self.url = url
        self.method = method
        self.headers = headers
        self.payload = payload
        self.encoding = encoding
        self.listeners = listeners or {}

    def _read(self):
        """Read the incoming event source stream and yield event chunks"""
        data = b""
        with self.client.stream(
            self.method,
            self.url,
            headers=self.headers,
            data=self.payload,
            timeout=None,
        ) as r:
            for chunk in r.iter_bytes():
                for line in chunk.splitlines(True):
                    data += line
                    if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                        yield data
                        data = b""

    def _events(self):
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

    def run(self):
        while not self.kill:
            try:
                for event in self._events():
                    if self.kill:
                        break
                    if event.event in self.listeners:
                        self.listeners[event.event](event)
            except Exception:
                self.kill = True


class SSEClient:
    """Implementation of a server side event client"""

    _listeners: dict[str, Callable[[Event], Any]]
    _loop_thread: EventLoop

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        encoding: str = "utf-8",
    ) -> None:
        self._listeners = {}
        self._loop_thread = EventLoop(
            url=url,
            method=method,
            headers=headers,
            payload=payload,
            encoding=encoding,
            listeners=self._listeners,
            name="loop",
        )
        self._loop_thread.daemon = True
        self._loop_thread.start()

    def add_event_listener(
        self, event: str, callback: Callable[[Any], None]
    ) -> None:
        self._listeners[event] = callback
        self._loop_thread.listeners = self._listeners

    def remove_event_listener(
        self, event: str, callback: Callable[[Any], None]
    ) -> None:
        if event in self._listeners:
            self._listeners.pop(event)
            self._loop_thread.listeners = self._listeners

    def close(self) -> None:
        # TODO: does not work like this
        self._loop_thread.kill = True
