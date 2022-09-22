from __future__ import annotations

from typing import Callable
import dataclasses
import json

from pocketbase.services.utils.base_service import BaseService
from pocketbase.services.utils.sse import Event, SSEClient
from pocketbase.models.record import Record


@dataclasses.dataclass
class MessageData:
    action: str
    record: Record


class Realtime(BaseService):
    subscriptions: dict
    client_id: str = ""
    event_source: SSEClient | None = None

    def __init__(self, client) -> None:
        super().__init__(client)
        self.subscriptions = {}
        self.client_id = ""
        self.event_source = None

    def subscribe(
        self, subscription: str, callback: Callable[[MessageData], None]
    ) -> None:
        """Inits the sse connection (if not already) and register the subscription."""
        # unsubscribe existing
        if subscription in self.subscriptions and self.event_source:
            self.event_source.remove_event_listener(subscription, callback)
        # register subscription
        self.subscriptions[subscription] = self._make_subscription(callback)
        if not self.event_source:
            self._connect()
        elif self.client_id:
            self._submit_subscriptions()

    def unsubscribe(self, subscription: str | None = None) -> None:
        """
        Unsubscribe from a subscription.

        If the `subscription` argument is not set,
        then the client will unsubscribe from all registered subscriptions.

        The related sse connection will be autoclosed if after the
        unsubscribe operations there are no active subscriptions left.
        """
        if not subscription:
            self._remove_subscription_listeners()
            self.subscriptions = {}
        elif subscription in self.subscriptions:
            self.event_source.remove_event_listener(
                subscription, self.subscriptions[subscription]
            )
            self.subscriptions.pop(subscription)
        else:
            return
        if self.client_id:
            self._submit_subscriptions()
        if not self.subscriptions:
            self._disconnect()

    def _make_subscription(
        self, callback: Callable[[MessageData], None]
    ) -> Callable[[Event], None]:
        def listener(event: Event) -> None:
            data = json.loads(event.data)
            if "record" in data and "action" in data:
                callback(
                    MessageData(
                        action=data["action"],
                        record=Record(
                            data=data["record"],
                        ),
                    )
                )

        return listener

    def _submit_subscriptions(self) -> bool:
        self._add_subscription_listeners()
        self.client.send(
            "/api/realtime",
            {
                "method": "POST",
                "body": {
                    "clientId": self.client_id,
                    "subscriptions": list(self.subscriptions.keys()),
                },
            },
        )
        return True

    def _add_subscription_listeners(self) -> None:
        if not self.event_source:
            return
        self._remove_subscription_listeners()
        for subscription, callback in self.subscriptions.items():
            self.event_source.add_event_listener(subscription, callback)

    def _remove_subscription_listeners(self) -> None:
        if not self.event_source:
            return
        for subscription, callback in self.subscriptions.items():
            self.event_source.remove_event_listener(subscription, callback)

    def _connect_handler(self, event: Event) -> None:
        self.client_id = event.id
        self._submit_subscriptions()

    def _connect(self) -> None:
        self._disconnect()
        self.event_source = SSEClient(self.client.build_url("/api/realtime"))
        self.event_source.add_event_listener("PB_CONNECT", self._connect_handler)

    def _disconnect(self) -> None:
        self._remove_subscription_listeners()
        self.client_id = ""
        if not self.event_source:
            return
        self.event_source.remove_event_listener("PB_CONNECT", self._connect_handler)
        self.event_source.close()
        self.event_source = None
