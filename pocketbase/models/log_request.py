from __future__ import annotations

from typing import Any

from pocketbase.models.utils.base_model import BaseModel


class LogRequest(BaseModel):
    url: str
    method: str
    status: int
    auth: str
    remote_ip: str
    user_ip: str
    referer: str
    user_agent: str
    meta: dict[str, Any]

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.url = data.get("url", "")
        self.method = data.get("method", "")
        self.status = data.get("status", 200)
        self.auth = data.get("auth", "guest")
        self.remote_ip = data.get("remoteIp", data.get("ip", ""))
        self.user_ip = data.get("userIp", "")
        self.referer = data.get("referer", "")
        self.user_agent = data.get("userAgent", "")
        self.meta = data.get("meta", {})
