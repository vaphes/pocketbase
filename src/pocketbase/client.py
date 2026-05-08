from __future__ import annotations

import datetime
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import httpx

from pocketbase.errors import ClientResponseError
from pocketbase.models import FileUpload
from pocketbase.services.backup_service import BackupService
from pocketbase.services.batch_service import BatchService
from pocketbase.services.collection_service import CollectionService
from pocketbase.services.cron_service import CronService
from pocketbase.services.file_service import FileService
from pocketbase.services.health_service import HealthService
from pocketbase.services.log_service import LogService
from pocketbase.services.realtime_service import RealtimeService
from pocketbase.services.record_service import RecordService
from pocketbase.services.settings_service import SettingsService
from pocketbase.stores.base_auth_store import AuthStoreProtocol, BaseAuthStore
from pocketbase.utils import deprecated

if TYPE_CHECKING:
    from pocketbase.models.record import Record

SendOptions = dict[str, Any]
SendResult = Any


class Client:
    before_send: (
        Callable[[str, SendOptions], tuple[str, SendOptions]] | None
    ) = None
    after_send: (
        Callable[[httpx.Response, SendResult, SendOptions], SendResult] | None
    ) = None

    def __init__(
        self,
        base_url: str = "/",
        lang: str = "en-US",
        auth_store: AuthStoreProtocol | None = None,
        auto_snake_case: bool = True,
        **kwargs: Any,
    ) -> None:
        self.base_url = base_url
        self.http_client = httpx.Client(base_url=base_url, **kwargs)
        self.lang = lang
        self.auth_store = auth_store or BaseAuthStore()  # LocalAuthStore()
        self.auto_snake_case = auto_snake_case
        # services
        self.backups = BackupService(self)
        self.collections = CollectionService(self)
        self.files = FileService(self)
        self.health = HealthService(self)
        self.logs = LogService(self)
        self.settings = SettingsService(self)
        self.realtime = RealtimeService(self)
        self.crons = CronService(self)
        self.record_services: dict[str, RecordService] = {}

    def _send(self, path: str, req_config: dict[str, Any]) -> httpx.Response:
        """Sends an api http request returning response object."""
        config: dict[str, Any] = {"method": "GET"}
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
        body: dict[str, Any] | None = config.get("body", None)
        # handle requests including files as multipart:
        data: dict[str, Any] | None = {}
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
            response: httpx.Response = self.http_client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=body,
                data=data,
                files=files,  # type: ignore
            )
        except Exception as e:
            raise ClientResponseError(
                f"General request error. Original error: {e}",
                original_error=e,
            )
        return response

    def build_url(self, path: str) -> str:
        """Builds a full client url by safely concatenating the provided path."""
        url = str(self.base_url)
        if not url.endswith("/"):
            url += "/"
        if path.startswith("/"):
            path = path[1:]
        return url + path

    def create_batch(self) -> BatchService:
        """Returns a new BatchService instance."""
        return BatchService(self)

    def collection(self, id_or_name: str) -> RecordService:
        """Returns the RecordService associated to the specified collection."""
        if id_or_name not in self.record_services:
            self.record_services[id_or_name] = RecordService(self, id_or_name)
        return self.record_services[id_or_name]

    def filter(self, raw: str, params: dict[str, Any] | None = None) -> str:
        """
        Constructs a filter expression with placeholders populated from a
        parameters object.

        Placeholder parameters are defined with the `{:paramName}` notation.

        The following parameter values are supported:

        - `str` (single quotes are autoescaped)
        - `bool`
        - `datetime.datetime` object (stringified into the PocketBase datetime format)
        - `None` (converted to `null`)
        - everything else is converted to a string using `str()`

        Example:

        ```
        pb.collection("example").get_first_list_item(pb.filter(
            'title ~ {:title} && created >= {:created}',
            { title: "example", created: datetime(2023, 1, 1) }
        ))
        ```
        """
        if not params:
            return raw
        for k, v in params.items():
            placeholder = "{:" + k + "}"
            if isinstance(v, str):
                v_escaped = v.replace("'", "\\'")
                raw = raw.replace(placeholder, f"'{v_escaped}'")
            elif isinstance(v, bool):
                raw = raw.replace(placeholder, "true" if v else "false")
            elif isinstance(v, datetime.datetime):
                raw = raw.replace(
                    placeholder, f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
                )
            elif v is None:
                raw = raw.replace(placeholder, "null")
            else:
                raw = raw.replace(placeholder, str(v))
        return raw

    def send(self, path: str, req_config: dict[str, Any]) -> SendResult:
        """Sends an api http request."""
        if self.before_send:
            path, req_config = self.before_send(path, req_config)
        response = self._send(path, req_config)
        try:
            data = response.json()
        except Exception:
            data = None
        if self.after_send:
            data = self.after_send(response, data, req_config)
        if response.status_code >= 400:
            raise ClientResponseError(
                f"Response error. Status code:{response.status_code}",
                url=str(response.url),
                status=response.status_code,
                data=data,
            )
        return data

    def send_raw(self, path: str, req_config: dict[str, Any]) -> bytes:
        """Sends an api http request returning raw bytes response."""
        response = self._send(path, req_config)
        return response.content

    # Deprecated methods and properties

    @property
    @deprecated
    def admins(self) -> RecordService:
        """
        **Deprecated!**

        With PocketBase v0.23.0 admins are converted to a regular auth
        collection named "_superusers", aka. you can use directly
        collection("_superusers").
        """
        return self.collection("_superusers")

    @deprecated
    def get_file_url(
        self,
        record: Record,
        filename: str,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        """
        **Deprecated!**

        Please use `pb.files.get_url()`
        """
        return self.files.get_url(record, filename, query_params)

    @deprecated
    def get_file_token(self) -> str:
        """
        **Deprecated!**

        Please use `pb.files.get_token()`
        """
        return self.files.get_token()
