from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError
from pocketbase.models.collection import Collection

from uuid import uuid4
import pytest


class TestCollectionService:
    def test_create(self, client: PocketBase, state):
        state.collection = client.collections.create(
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
        assert isinstance(state.collection, Collection)
        assert state.collection.is_base
        assert not state.collection.is_auth()
        assert not state.collection.is_single()

    def test_update(self, client: PocketBase, state):
        client.collections.update(
            state.collection.id,
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

    def test_delete(self, client: PocketBase, state):
        client.collections.delete(state.collection.id)
        with pytest.raises(ClientResponseError) as exc:
            client.collections.delete(state.collection.id, uuid4().hex)
        assert exc.value.status == 404  # double already deleted


def test_delete_nonexisting_exception(client):
    with pytest.raises(ClientResponseError) as exc:
        client.collections.delete(uuid4().hex, uuid4().hex)
    assert exc.value.status == 404  # delete nonexisting


def test_get_nonexisting_exception(client):
    with pytest.raises(ClientResponseError) as exc:
        client.collections.get_one(uuid4().hex)
    assert exc.value.status == 404


def test_import_collection(client):
    data = [
        {
            "name": uuid4().hex,
            "schema": [
                {
                    "name": "status",
                    "type": "bool",
                },
            ],
        },
        {
            "name": uuid4().hex,
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                },
            ],
        },
    ]
    assert client.collections.import_collections(data)
