from __future__ import annotations

from pocketbase.models import Backup
from pocketbase.services.utils import BaseService


class BackupsService(BaseService):
    def decode(self, data: dict) -> Backup:
        return Backup(data)

    def base_path(self) -> str:
        return "/api/backups"

    def create(self, name: str):
        # The backups service create method does not return an object.
        self.client.send(
            self.base_path(),
            {"method": "POST", "body": {"name": name}},
        )

    def get_full_list(self, query_params: dict = {}) -> list[Backup]:
        response_data = self.client.send(self.base_path(), {"method": "GET", "params": query_params})
        return [self.decode(item) for item in response_data]

    def download(self, key: str, file_token: str = None) -> bytes:
        if file_token is None:
            file_token = self.client.get_file_token()
        return self.client.send_raw("%s/%s" % (self.base_path(), key),
                                    {"method": "GET", "params": {"token": file_token}})

    def delete(self, key: str):
        self.client.send("%s/%s" % (self.base_path(), key), {"method": "DELETE"})
