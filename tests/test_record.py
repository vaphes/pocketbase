from .connection import client, state, PocketBase

__all__ = ("client", "state")
from pocketbase.utils import ClientResponseError
from pocketbase.client import FileUpload
import httpx
from random import getrandbits

from uuid import uuid4
import pytest


class TestRecordService:
    def test_init_collection(self, client: PocketBase, state):
        srv = client.collections
        # create collection
        schema = [
            {
                "name": "title",
                "type": "text",
                "required": True,
            },
            {
                "name": "image",
                "type": "file",
                "required": True,
                "options": {
                    "maxSelect": 3,
                    "maxSize": 5242880,
                    "mimeTypes": [
                        "application/octet-stream",
                        "text/plain",
                    ],
                },
            },
        ]
        state.coll = srv.create(
            {
                "name": uuid4().hex,
                "type": "base",
                "schema": schema,
            }
        )
        schema.append(
            {
                "name": "rel",
                "type": "relation",
                "required": False,
                "options": {
                    "collectionId": state.coll.id,
                    "cascadeDelete": False,
                    "maxSelect": 1,
                },
            },
        )
        state.coll = srv.update(state.coll.id, {"schema": schema})

    def test_create_record(self, client: PocketBase, state):
        bname = uuid4().hex
        state.bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")
        state.record = client.collection(state.coll.id).create(
            {
                "title": uuid4().hex,
                "image": FileUpload(
                    ("a.txt", b"a.txt CONTENT", "text/plain"),
                    (bname + ".txt", state.bcontent, "application/octet-stream"),
                    ("c.txt", b"c.txt CONTENT", "text/plain"),
                ),
            }
        )
        for fn in state.record.image:
            if fn.startswith(bname):
                break
        assert fn.startswith(bname)
        state.bfilename = fn

    def test_create_multiple_record(self, client: PocketBase, state):
        state.chained_records = [
            state.record.id,
        ]
        for _ in range(10):
            state.chained_records.append(
                client.collection(state.coll.id)
                .create(
                    {
                        "title": uuid4().hex,
                        "rel": state.chained_records[-1],
                        "image": FileUpload(
                            uuid4().hex, b"a.txt CONTENT", "text/plain"
                        ),
                    }
                )
                .id
            )

    def test_get_record(self, client: PocketBase, state):
        state.get_record = client.collection(state.coll.id).get_one(state.record.id)
        assert state.get_record.title is not None
        assert state.record.title == state.get_record.title
        assert state.record.image == state.get_record.image
        assert not state.get_record.is_new
        assert state.get_record.id in f"{state.get_record}"
        assert state.get_record.id in repr(state.get_record)

    def test_get_record_expand(self, client: PocketBase, state):
        rel = client.collection(state.coll.id).get_one(
            state.chained_records[-1], {"expand": "rel.rel.rel.rel.rel.rel"}
        )
        for i, r in enumerate(reversed(state.chained_records)):
            assert rel.id == r
            if i > 5:
                break
            rel = rel.expand["rel"]

    def test_get_list(self, client: PocketBase, state):
        val = client.collection(state.coll.id).get_list()
        assert len(val.items) > 10

    def test_get_full_list(self, client: PocketBase, state):
        items = client.collection(state.coll.id).get_full_list(batch=1)
        cnt = 0
        for i in items:
            if i.title == state.get_record.title:
                cnt += 1
        assert cnt == 1

    def test_update_record(self, client: PocketBase, state):
        assert state.record.title == state.get_record.title
        state.get_record = client.collection(state.coll.id).update(
            state.record.id, {"title": uuid4().hex}
        )
        assert state.record.title != state.get_record.title

    def test_remove_file_from_record(self, client: PocketBase, state):
        assert state.record.image == state.get_record.image
        # delete some of the files from record but keep the file named "state.filename"
        state.get_record = client.collection(state.coll.id).update(
            state.record.id, {"image": [state.bfilename]}
        )
        assert state.record.image != state.get_record.image

    def test_retrieve_file(self, client: PocketBase, state):

        r = httpx.get(
            client.collection(state.coll.id).get_file_url(
                state.get_record, state.bfilename
            )
        )
        assert r.status_code == 200
        assert r.content == state.bcontent

    def test_delete_record(self, client: PocketBase, state):
        client.collection(state.coll.id).delete(state.record.id)
        # deleting already deleted record should give 404
        with pytest.raises(ClientResponseError) as exc:
            client.collection(state.coll.id).get_one(state.record.id)
        assert exc.value.status == 404

    def test_delete_nonexisting_exception(self, client: PocketBase, state):
        with pytest.raises(ClientResponseError) as exc:
            client.collection(state.coll.id).delete(uuid4().hex, uuid4().hex)
        assert exc.value.status == 404  # delete nonexisting

    def test_get_nonexisting_exception(self, client: PocketBase, state):
        with pytest.raises(ClientResponseError) as exc:
            client.collection(state.coll.id).get_one(uuid4().hex)
        assert exc.value.status == 404
