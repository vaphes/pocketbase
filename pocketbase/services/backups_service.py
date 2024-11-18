from __future__ import annotations

from typing import Any

from pocketbase.models import Backup, FileUpload
from pocketbase.services.utils import BaseService


class BackupsService(BaseService):
    def decode(self, data: dict[str, Any]) -> Backup:
        return Backup(data)

    def base_path(self) -> str:
        return "/api/backups"

    def create(self, name: str):
        # The backups service create method does not return an object.
        self.client.send(
            self.base_path(),
            {"method": "POST", "body": {"name": name}},
        )

    def get_full_list(self, query_params: dict[str, Any] = {}) -> list[Backup]:
        response_data = self.client.send(
            self.base_path(), {"method": "GET", "params": query_params}
        )
        return [self.decode(item) for item in response_data]

    def download(self, key: str, file_token: str | None = None) -> bytes:
        if file_token is None:
            file_token = self.client.get_file_token()
        return self.client.send_raw(
            "%s/%s" % (self.base_path(), key),
            {"method": "GET", "params": {"token": file_token}},
        )

    def delete(self, key: str):
        self.client.send(
            "%s/%s" % (self.base_path(), key), {"method": "DELETE"}
        )

    def restore(self, key: str):
        self.client.send(
            "%s/%s/restore" % (self.base_path(), key), {"method": "POST"}
        )

    def upload(self, file_upload: FileUpload):
        self.client.send(
            self.base_path() + "/upload",
            {"method": "POST", "body": {"file": file_upload}},
        )
