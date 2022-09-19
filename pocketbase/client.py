from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from pocketbase.services.admins import Admins
from pocketbase.services.collections import Collections
from pocketbase.services.logs import Logs
from pocketbase.services.realtime import Realtime
from pocketbase.services.records import Records
from pocketbase.services.users import Users
from pocketbase.services.settings import Settings
from pocketbase.stores.base_auth_store import BaseAuthStore

# from pocketbase.stores.local_auth_store import LocalAuthStore


class ClientResponseError(Exception):
    url: str = ""
    status: int = 0
    data: dict = {}
    is_abort: bool = False
    original_error: Any = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)
        self.url = kwargs.get("url", "")
        self.status = kwargs.get("status", 0)
        self.data = kwargs.get("data", {})
        self.is_abort = kwargs.get("is_abort", False)
        self.original_error = kwargs.get("original_error", None)


class Client:
    base_url: str
    lang: str
    auth_store: BaseAuthStore
    settings: Settings
    admins: Admins
    users: Users
    collections: Collections
    records: Records
    logs: Logs
    realtime: Realtime

    def __init__(
        self,
        base_url: str = "/",
        lang: str = "en-US",
        auth_store: BaseAuthStore = None,
    ) -> None:
        self.base_url = base_url
        self.lang = lang
        self.auth_store = auth_store or BaseAuthStore()  # LocalAuthStore()
        # services
        self.admins = Admins(self)
        self.users = Users(self)
        self.records = Records(self)
        self.collections = Collections(self)
        self.logs = Logs(self)
        self.settings = Settings(self)
        self.realtime = Realtime(self)

    def cancel_request(self, cancel_key: str):
        return self

    def cancel_all_requests(self):
        return self

    def send(self, path: str, req_config: dict[str:Any]) -> Any:
        """Sends an api http request."""
        config = {"method": "GET"}
        config.update(req_config)
        # check if Authorization header can be added
        if self.auth_store.token and (
            not "headers" in config or "Authorization" not in config["headers"]
        ):
            auth_type = "Admin"
            if hasattr(self.auth_store.model, "verified"):
                auth_type = "User"
            config["headers"] = config.get("headers", {})
            config["headers"].update(
                {"Authorization": f"{auth_type} {self.auth_store.token}"}
            )
        # build url + path
        url = self.build_url(path)
        # send the request
        method = config.get("method", "GET")
        params = config.get("params", None)
        headers = config.get("headers", None)
        body = config.get("body", None)
        try:
            response = httpx.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=body,
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

    def build_url(self, path: str) -> str:
        url = self.base_url
        if not self.base_url.endswith("/"):
            url += "/"
        if path.startswith("/"):
            path = path[1:]
        return url + path


if __name__ == "__main__":
    from pocketbase.stores.local_auth_store import LocalAuthStore

    pb = Client(base_url="http://ares.olimpo:8090/", auth_store=LocalAuthStore())
    # pb.admins.auth_via_email("vaphes@gmail.com", "vaphes2007")
    print(pb.auth_store.token)
    books = pb.collections.get_one("books")
    print("ok")
    # sacd = "nwvgaw6iiibv4fp"
    # book = {
    #     "author": sacd,
    #     "name": "A study in red",
    #     "rating": 4.5,
    #     "summary": "The worst Sherlock Homes book",
    # }
    # data = pb.records.create("books", book)
    # print(data)
