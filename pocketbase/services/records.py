from __future__ import annotations

from urllib.parse import quote, urlencode

from pocketbase.services.utils.sub_crud_service import SubCrudService
from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.record import Record


class Records(SubCrudService):
    def decode(self, data: dict) -> BaseModel:
        return Record(data)

    def base_crud_path(self, collection_id_or_name: str) -> str:
        return "/api/collections/" + quote(collection_id_or_name) + "/records"

    def get_file_url(
        self, record: Record, filename: str, query_params: dict = {}
    ) -> str:
        """Builds and returns an absolute record file url."""
        base_url = self.client.base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        result = f"{base_url}/api/files/{record.collection_id}/{record.id}/{filename}"
        if query_params:
            result += "?" + urlencode(query_params)
        return result
