from __future__ import annotations

from abc import ABC

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.utils.list_result import ListResult
from pocketbase.services.utils.base_crud_service import BaseCrudService


class CrudService(BaseCrudService, ABC):
    def base_crud_path(self) -> str:
        """Base path for the crud actions (without trailing slash, eg. '/admins')."""

    def get_full_list(
        self, batch_size: int = 100, query_params: dict = {}
    ) -> list[BaseModel]:
        return self._get_full_list(self.base_crud_path(), batch_size, query_params)

    def get_list(
        self, page: int = 1, per_page: int = 30, query_params: dict = {}
    ) -> ListResult:
        return self._get_list(self.base_crud_path(), page, per_page, query_params)

    def get_one(self, id: str, query_params: dict = {}) -> BaseModel:
        return self._get_one(self.base_crud_path(), id, query_params)

    def create(self, body_params: dict = {}, query_params: dict = {}) -> BaseModel:
        return self._create(self.base_crud_path(), body_params, query_params)

    def update(
        self, id: str, body_params: dict = {}, query_params: dict = {}
    ) -> BaseModel:
        return self._update(self.base_crud_path(), id, body_params, query_params)

    def delete(self, id: str, query_params: dict = {}) -> bool:
        return self._delete(self.base_crud_path(), id, query_params)
