from __future__ import annotations

from abc import ABC
from urllib.parse import quote
from pocketbase.utils import ClientResponseError

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.utils.list_result import ListResult
from pocketbase.services.utils.base_service import BaseService


class BaseCrudService(BaseService, ABC):
    def decode(self, data: dict) -> BaseModel:
        """Response data decoder"""

    def _get_full_list(
        self, base_path: str, batch_size: int = 100, query_params: dict = {}
    ) -> list[BaseModel]:
        result: list[BaseModel] = []

        def request(result: list[BaseModel], page: int) -> list:
            list = self._get_list(base_path, page, batch_size, query_params)
            items = list.items
            total_items = list.total_items
            result += items
            if len(items) > 0 and total_items > len(result):
                return request(result, page + 1)
            return result

        return request(result, 1)

    def _get_list(
        self, base_path: str, page: int = 1, per_page: int = 30, query_params: dict = {}
    ) -> ListResult:
        query_params.update({"page": page, "perPage": per_page})
        response_data = self.client.send(
            base_path, {"method": "GET", "params": query_params}
        )
        items: list[BaseModel] = []
        if "items" in response_data:
            response_data["items"] = response_data["items"] or []
            for item in response_data["items"]:
                items.append(self.decode(item))
        return ListResult(
            response_data.get("page", 1),
            response_data.get("perPage", 0),
            response_data.get("totalItems", 0),
            response_data.get("totalPages", 0),
            items,
        )

    def _get_one(self, base_path: str, id: str, query_params: dict = {}) -> BaseModel:
        return self.decode(
            self.client.send(
                f"{base_path}/{quote(id)}", {"method": "GET", "params": query_params}
            )
        )

    def _get_first_list_item(self, base_path: str, filter: str, query_params={}):
        query_params.update(
            {
                "filter": filter,
                "$cancelKey": "one_by_filter_" + base_path + "_" + filter,
            }
        )
        result = self._get_list(base_path, 1, 1, query_params)
        if not result.items:
            raise ClientResponseError(
                "The requested resource wasn't found.", status=404
            )
        return result.items[0]

    def _create(
        self, base_path: str, body_params: dict = {}, query_params: dict = {}
    ) -> BaseModel:
        return self.decode(
            self.client.send(
                base_path,
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def _update(
        self, base_path: str, id: str, body_params: dict = {}, query_params: dict = {}
    ) -> BaseModel:
        return self.decode(
            self.client.send(
                f"{base_path}/{quote(id)}",
                {"method": "PATCH", "params": query_params, "body": body_params},
            )
        )

    def _delete(self, base_path: str, id: str, query_params: dict = {}) -> bool:
        self.client.send(
            f"{base_path}/{quote(id)}", {"method": "DELETE", "params": query_params}
        )
        return True
