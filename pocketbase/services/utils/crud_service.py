from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from urllib.parse import quote

from pocketbase.errors import ClientResponseError
from pocketbase.models.utils.base_model import Model
from pocketbase.models.utils.list_result import ListResult
from pocketbase.services.utils.base_service import BaseService

T = TypeVar("T", bound=Model)


class CrudService(Generic[T], BaseService, ABC):
    @abstractmethod
    def base_crud_path(self) -> str:
        """Base path for the crud actions (without trailing slash, eg. '/admins')."""

    @abstractmethod
    def decode(self, data: dict[str, Any]) -> T:
        """Response data decoder"""

    def get_full_list(
        self,
        batch: int = 100,
        query_params: dict[str, Any] | None = None,
    ) -> list[T]:
        result: list[T] = []

        def request(result: list[T], page: int) -> list[T]:
            list = self.get_list(page, batch, query_params)
            items = list.items
            total_items = list.total_items
            result += items
            if len(items) > 0 and total_items > len(result):
                return request(result, page + 1)
            return result

        return request(result, 1)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 30,
        query_params: dict[str, Any] | None = None,
    ) -> ListResult[T]:
        query_params = query_params or {}
        query_params.update({"page": page, "perPage": per_page})
        response_data = self.client.send(
            self.base_crud_path(), {"method": "GET", "params": query_params}
        )
        items: list[T] = []
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

    def get_one(
        self,
        id: str,
        query_params: dict[str, Any] | None = None,
    ) -> T:
        return self.decode(
            self.client.send(
                f"{self.base_crud_path()}/{quote(id)}",
                {"method": "GET", "params": query_params},
            )
        )

    def get_first_list_item(
        self,
        filter: str,
        query_params: dict[str, Any] | None = None,
    ):
        """
        Returns the first found item by the specified filter.

        Internally it calls `getList(1, 1, { filter })` and returns the
        first found item.

        For consistency with `getOne`, this method will throw a 404
        ClientResponseError if no item was found.
        """
        query_params = query_params or {}
        query_params.update(
            {
                "filter": filter,
                "$cancelKey": "one_by_filter_"
                + self.base_crud_path()
                + "_"
                + filter,
            }
        )
        result = self.get_list(1, 1, query_params)
        if not result.items:
            raise ClientResponseError(
                "The requested resource wasn't found.", status=404
            )
        return result.items[0]

    def create(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> T:
        return self.decode(
            self.client.send(
                self.base_crud_path(),
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def update(
        self,
        id: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> T:
        return self.decode(
            self.client.send(
                f"{self.base_crud_path()}/{quote(id)}",
                {
                    "method": "PATCH",
                    "params": query_params,
                    "body": body_params,
                },
            )
        )

    def delete(
        self,
        id: str,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        self.client.send(
            f"{self.base_crud_path()}/{quote(id)}",
            {"method": "DELETE", "params": query_params},
        )
        return True
