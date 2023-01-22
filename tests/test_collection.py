from .connection import get_client_connection
from pocketbase.utils import ClientResponseError

from uuid import uuid4
import pytest


def test_crud():
    client = get_client_connection(logged_in_as_master_admin=True)

    srv = client.collections
    created_collection = srv.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "options": {
                        "min": 10,
                    },
                },
            ],
        }
    )
    srv.update(
        created_collection.id,
        {
            "name": uuid4().hex,
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "options": {
                        "min": 10,
                    },
                },
                {
                    "name": "status",
                    "type": "bool",
                },
            ],
        },
    )

    srv.delete(created_collection.id)


def test_crud_exceptions():
    client = get_client_connection(logged_in_as_master_admin=True)
    srv = client.collections
    with pytest.raises(ClientResponseError) as exc:
        srv.delete(uuid4().hex, uuid4().hex)
    assert exc.value.status == 404
