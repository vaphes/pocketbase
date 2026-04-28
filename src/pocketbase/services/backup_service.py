from __future__ import annotations

from typing import Any

from pocketbase.models import Backup, FileUpload
from pocketbase.services.base_service import BaseService


class BackupService(BaseService):
    def decode(self, data: dict[str, Any]) -> Backup:
        return Backup(data)

    def create(self, name: str) -> bool:
        """Initializes a new backup."""
        self.client.send(
            "/api/backups",
            {"method": "POST", "body": {"name": name}},
        )
        return True

    def delete(self, key: str) -> bool:
        """Deletes a single backup file."""
        self.client.send(f"/api/backups/{key}", {"method": "DELETE"})
        return True

    def download(self, key: str, file_token: str | None = None) -> bytes:
        """Downloads a single existing backup using a superuser file token."""
        if file_token is None:
            file_token = self.client.files.get_token()
        return self.client.send_raw(
            f"/api/backups/{key}",
            {"method": "GET", "params": {"token": file_token}},
        )

    def get_download_url(self, key: str, file_token: str | None = None) -> str:
        """
        Builds a download url for a single existing backup using a superuser
        file token and the backup file key.
        """
        if file_token is None:
            file_token = self.client.files.get_token()
        return self.client.build_url(f"/api/backups/{key}?token={file_token}")

    def get_full_list(self, query_params: dict[str, Any] = {}) -> list[Backup]:
        """Returns list with all available backup files."""
        response_data = self.client.send(
            "/api/backups", {"method": "GET", "params": query_params}
        )
        return [self.decode(item) for item in response_data]

    def restore(self, key: str) -> bool:
        """Initializes an app data restore from an existing backup."""
        self.client.send(f"/api/backups/{key}/restore", {"method": "POST"})
        return True

    def upload(self, file_upload: FileUpload) -> bool:
        """Uploads an existing backup file."""
        self.client.send(
            "/api/backups/upload",
            {"method": "POST", "body": {"file": file_upload}},
        )
        return True
