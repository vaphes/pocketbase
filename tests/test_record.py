from .connection import client, state

__all__ = ("client", "state")
from pocketbase.utils import ClientResponseError
from pocketbase.client import FileUpload
import httpx
from random import getrandbits

from uuid import uuid4
import pytest


class TestRecordService:
    def test_init_collection(self, client, state):
        srv = client.collections
        # create collection
        coll = srv.create(
            {
                "name": uuid4().hex,
                "type": "base",
                "schema": [
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
                ],
            }
        )

        state.srv = client.collection(coll.id)

    def test_create_record(self, state):
        bname = uuid4().hex
        state.bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")
        state.record = state.srv.create(
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

    def test_get_record(self, state):
        state.get_record = state.srv.get_one(state.record.id)
        assert state.record.image == state.get_record.image

    def test_update_record(self, state):
        assert state.record.title == state.get_record.title
        state.get_record = state.srv.update(state.record.id, {"title": uuid4().hex})
        assert state.record.title != state.get_record.title

    def test_remove_file_from_record(self, state):
        assert state.record.image == state.get_record.image
        # delete some of the files from record but keep the file named "state.filename"
        state.get_record = state.srv.update(
            state.record.id, {"image": [state.bfilename]}
        )
        assert state.record.image != state.get_record.image

    def test_retrieve_file(self, state):

        r = httpx.get(state.srv.get_file_url(state.get_record, state.bfilename))
        assert r.status_code == 200
        assert r.content == state.bcontent

    def test_delete_record(self, state):
        state.srv.delete(state.record.id)
        # deleting already deleted record should give 404
        with pytest.raises(ClientResponseError) as exc:
            state.srv.get_one(state.record.id)
        assert exc.value.status == 404

    def test_delete_nonexisting_exception(self, state):
        with pytest.raises(ClientResponseError) as exc:
            state.srv.delete(uuid4().hex, uuid4().hex)
        assert exc.value.status == 404  # delete nonexisting

    def test_get_nonexisting_exception(self, state):
        with pytest.raises(ClientResponseError) as exc:
            state.srv.get_one(uuid4().hex)
        assert exc.value.status == 404
