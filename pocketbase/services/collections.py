from typing import Any

from pocketbase.services.utils.crud_service import CrudService
from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.collection import Collection


class Collections(CrudService):
    def decode(self, data: dict[str:Any]) -> BaseModel:
        return Collection(data)

    def base_crud_path(self) -> str:
        return "/api/collections"

    def import_collections(
        self,
        collections: list[Collection],
        delete_missing: bool = False,
        query_params: dict = {},
    ) -> bool:
        """
        Imports the provided collections.

        If `delete_missing` is `True`, all local collections and schema fields,
        that are not present in the imported configuration, WILL BE DELETED
        (including their related records data)!
        """
        self.client.send(
            self.base_crud_path() + "/import",
            {
                "method": "PUT",
                "params": query_params,
                "body": {"collections": collections, "deleteMissing": delete_missing},
            },
        )
        return True
