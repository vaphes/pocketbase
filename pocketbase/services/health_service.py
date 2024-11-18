from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pocketbase.services.utils import BaseService


@dataclass
class HealthCheckResponse:
    code: int
    message: str
    data: dict[str, Any]


class HealthService(BaseService):
    def check(
        self, query_params: dict[str, Any] | None = None
    ) -> HealthCheckResponse:
        query_params = query_params or {}
        res = self.client.send(
            "/api/health", req_config={"method": "GET", "params": query_params}
        )
        return HealthCheckResponse(
            code=res.get("code"),
            message=res.get("message"),
            data=res.get("data", {}),
        )
