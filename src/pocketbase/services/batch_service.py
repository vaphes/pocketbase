import json
from typing import Any, TypedDict

from pocketbase.services.base_service import BaseService


class BatchRequest(TypedDict):
    method: str
    url: str
    json: dict[str, Any] | None
    files: dict[str, list[Any]] | None
    headers: dict[str, str] | None


class BatchRequestResult(TypedDict):
    status_code: int
    content: bytes | None


class SubBatchService:
    def __init__(
        self, requests: list[BatchRequest], collection_id_or_name: str
    ) -> None:
        self.requests = requests
        self.collection_id_or_name = collection_id_or_name

    def upsert(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> None:
        """
        Registers a record upsert request into the current batch queue.

        The request will be executed as update if `body_params` have a valid
        existing record `id` value, otherwise - create.
        """
        self.requests.append(
            {
                "method": "PUT",
                "url": f"/api/collections/{self.collection_id_or_name}/records",
                "json": body_params,
                "files": None,  # TODO: support file uploads
                "headers": query_params,
            }
        )

    def create(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> None:
        """Registers a record create request into the current batch queue."""
        self.requests.append(
            {
                "method": "POST",
                "url": f"/api/collections/{self.collection_id_or_name}/records",
                "json": body_params,
                "files": None,  # TODO: support file uploads
                "headers": query_params,
            }
        )

    def update(
        self,
        record_id: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> None:
        """Registers a record update request into the current batch queue."""
        self.requests.append(
            {
                "method": "PATCH",
                "url": f"/api/collections/{self.collection_id_or_name}/records/{record_id}",
                "json": body_params,
                "files": None,  # TODO: support file uploads
                "headers": query_params,
            }
        )

    def delete(
        self,
        record_id: str,
        query_params: dict[str, Any] | None = None,
    ) -> None:
        """Registers a record delete request into the current batch queue."""
        self.requests.append(
            {
                "method": "DELETE",
                "url": f"/api/collections/{self.collection_id_or_name}/records/{record_id}",
                "json": None,
                "files": None,
                "headers": query_params,
            }
        )


class BatchService(BaseService):
    def __init__(self, client) -> None:
        super().__init__(client)
        self.requests: list[BatchRequest] = []
        self.subs: dict[str, SubBatchService] = {}

    def collection(self, id_or_name: str) -> SubBatchService:
        """Starts constructing a batch request entry for the specified collection."""
        if id_or_name not in self.subs:
            self.subs[id_or_name] = SubBatchService(self.requests, id_or_name)
        return self.subs[id_or_name]

    def send(self) -> list[BatchRequestResult]:
        """Sends the batch requests."""
        form_data = {}
        json_data = []
        for i, req in enumerate(self.requests):
            json_data.append(
                {
                    "method": req["method"],
                    "url": req["url"],
                    "headers": req["headers"],
                    "body": req["json"],
                }
            )
            if req["files"] is not None:
                for file_key, file_values in req["files"].items():
                    for file_value in file_values:
                        form_data[f"requests.{i}.{file_key}"] = file_value

        form_data["@jsonPayload"] = json.dumps({"requests": json_data})

        return self.client.send(
            "/api/batch",
            {
                "method": "POST",
                "body": form_data,
            },
        )
