from __future__ import annotations

from typing import Any, Dict
from urllib.parse import quote, urlencode

import httpx

from pocketbase.models import FileUpload
from pocketbase.models.record import Record
from pocketbase.services.admin_service import AdminService
from pocketbase.services.collection_service import CollectionService
from pocketbase.services.log_service import LogService
from pocketbase.services.realtime_service import RealtimeService
from pocketbase.services.record_service import RecordService
from pocketbase.services.settings_service import SettingsService
from pocketbase.stores.base_auth_store import BaseAuthStore
from pocketbase.utils import ClientResponseError


class Client:
    base_url: str
    lang: str
    auth_store: BaseAuthStore
    settings: SettingsService
    admins: AdminService
    records: Record
    collections: CollectionService
    records: RecordService
    logs: LogService
    realtime: RealtimeService
    record_service: Dict[str, RecordService]

    def __init__(
        self,
        base_url: str = "/",
        lang: str = "en-US",
        auth_store: BaseAuthStore | None = None,
    ) -> None:
        self.base_url = base_url
        self.lang = lang
        self.auth_store = auth_store or BaseAuthStore()  # LocalAuthStore()
        # services
        self.admins = AdminService(self)
        self.collections = CollectionService(self)
        self.logs = LogService(self)
        self.settings = SettingsService(self)
        self.realtime = RealtimeService(self)
        self.record_service = {}

    def collection(self, id_or_name: str) -> RecordService:
        """Returns the RecordService associated to the specified collection."""
        if id_or_name not in self.record_service:
            self.record_service[id_or_name] = RecordService(self, id_or_name)
        return self.record_service[id_or_name]

    def send(self, path: str, req_config: dict[str:Any]) -> Any:
        """Sends an api http request."""
        config = {"method": "GET"}
        config.update(req_config)
        # check if Authorization header can be added
        if self.auth_store.token and (
            "headers" not in config or "Authorization" not in config["headers"]
        ):
            config["headers"] = config.get("headers", {})
            config["headers"].update({"Authorization": self.auth_store.token})
        # build url + path
        url = self.build_url(path)
        # send the request
        method = config.get("method", "GET")
        params = config.get("params", None)
        headers = config.get("headers", None)
        body = config.get("body", None)
        # handle requests including files as multipart:
        data = {}
        files = ()
        for k, v in (body if isinstance(body, dict) else {}).items():
            if isinstance(v, FileUpload):
                files += v.get(k)
            else:
                data[k] = v
        if len(files) > 0:
            # discard body, switch to multipart encoding
            body = None
        else:
            # discard files+data (do not use multipart encoding)
            files = None
            data = None
        try:
            response = httpx.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=body,
                data=data,
                files=files,
                timeout=120,
            )
        except Exception as e:
            raise ClientResponseError(
                f"General request error. Original error: {e}",
                original_error=e,
            )
        try:
            data = response.json()
        except Exception:
            data = None
        if response.status_code >= 400:
            raise ClientResponseError(
                f"Response error. Status code:{response.status_code}",
                url=response.url,
                status=response.status_code,
                data=data,
            )
        return data

    def get_file_url(self, record: Record, filename: str, query_params: dict):
        parts = [
            "api",
            "files",
            quote(record.collection_id or record.collection_name),
            quote(record.id),
            quote(filename),
        ]
        result = self.build_url("/".join(parts))
        if len(query_params) != 0:
            params: str = urlencode(query_params)
            result += "&" if "?" in result else "?"
            result += params
        return result

    def build_url(self, path: str) -> str:
        url = self.base_url
        if not self.base_url.endswith("/"):
            url += "/"
        if path.startswith("/"):
            path = path[1:]
        return url + path
