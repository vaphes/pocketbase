from __future__ import annotations

from dataclasses import dataclass
from typing import Union
from urllib.parse import quote
import datetime

from pocketbase.services.utils.base_service import BaseService
from pocketbase.models.utils.list_result import ListResult
from pocketbase.models.log_request import LogRequest
from pocketbase.utils import to_datetime


@dataclass
class HourlyStats:
    total: int
    date: Union[str, datetime.datetime]


class LogService(BaseService):
    def get_list(
        self, page: int = 1, per_page: int = 30, query_params: dict = {}
    ) -> ListResult:
        """Returns paginated logged requests list."""
        query_params.update({"page": page, "perPage": per_page})
        response_data = self.client.send(
            "/api/logs/",
            {"method": "GET", "params": query_params},
        )
        items: list[LogRequest] = []
        if "items" in response_data:
            response_data["items"] = response_data["items"] or []
            for item in response_data["items"]:
                items.append(LogRequest(item))
        return ListResult(
            response_data.get("page", 1),
            response_data.get("perPage", 0),
            response_data.get("totalItems", 0),
            response_data.get("totalPages", 0),
            items,
        )

    def get(self, id: str, query_params: dict = {}) -> LogRequest:
        """Returns a single logged request by its id."""
        return LogRequest(
            self.client.send(
                "/api/logs/" + quote(id),
                {"method": "GET", "params": query_params},
            )
        )

    def get_stats(self, query_params: dict = {}) -> list[HourlyStats]:
        """Returns request logs statistics."""
        return [
            HourlyStats(total=stat["total"], date=to_datetime(stat["date"]))
            for stat in self.client.send(
                "/api/logs/stats",
                {"method": "GET", "params": query_params},
            )
        ]
