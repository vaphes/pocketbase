from __future__ import annotations

from typing import Callable, Optional
from pocketbase.services.utils.base_service import BaseService
from pocketbase.models.record import Record


class Realtime(BaseService):
    client_id: str
    subscriptions: dict

    def subscribe(self, subscription: str, callback: Callable) -> None:
        """Inits the sse connection (if not already) and register the subscription."""
        self.subscriptions[subscription] = callback

    def unsubscribe(self, subscription: Optional[str] = None) -> None:
        """
        Unsubscribe from a subscription.

        If the `subscription` argument is not set,
        then the client will unsubscribe from all registered subscriptions.

        The related sse connection will be autoclosed if after the
        unsubscribe operations there are no active subscriptions left.
        """
        pass

    def _submit_subscriptions(self) -> bool:
        self.client.send(
            "/api/realtime",
            {
                "method": "POST",
                "body": {
                    "clientId": self.client_id,
                    "subscriptions": self.subscriptions.keys(),
                },
            },
        )
        return True

    def _add_subscription_listeners(self) -> None:
        pass

    def _remove_subscription_listeners(self) -> None:
        pass

    def _connect(self) -> None:
        pass

    def _disconnect(self) -> None:
        pass
