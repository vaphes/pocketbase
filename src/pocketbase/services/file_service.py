from __future__ import annotations

from typing import Any
from urllib.parse import quote, urlencode

from pocketbase.models.record import Record
from pocketbase.services.base_service import BaseService


class FileService(BaseService):
    def get_url(
        self,
        record: Record,
        filename: str,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        """Builds and returns an absolute record file url for the provided filename."""
        query_params = query_params or {}
        parts = [
            "api",
            "files",
            quote(record.collection_id or record.collection_name),
            quote(record.id),
            quote(filename),
        ]
        result = self.client.build_url("/".join(parts))
        if len(query_params) != 0:
            params: str = urlencode(query_params)
            result += "&" if "?" in result else "?"
            result += params
        return result

    def get_token(self) -> str:
        """Requests a new private file access token for the current auth model."""
        result = self.client.send(
            "/api/files/token", req_config={"method": "POST"}
        )
        return result.get("token", "")
