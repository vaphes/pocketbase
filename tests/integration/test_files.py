from pocketbase import PocketBase
from pocketbase.client import FileUpload
import httpx
from random import getrandbits
from uuid import uuid4


class TestFileService:
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
                "required": False,
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

    def test_create_three_file_record(self, client: PocketBase, state):
        name1 = uuid4().hex
        name2 = uuid4().hex
        name3 = uuid4().hex
        acontent = uuid4().hex
        bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")
        ccontent = uuid4().hex
        record = client.collection(state.coll.id).create(
            {
                "title": uuid4().hex,
                "image": FileUpload(
                    (name1 + ".txt", acontent, "text/plain"),
                    (name2 + ".txt", bcontent, "application/octet-stream"),
                    (name3 + ".txt", ccontent, "text/plain"),
                ),
            }
        )
        state.recordid = record.id
        assert len(record.image) == 3
        for fn in record.image:
            if fn.startswith(name2):
                break
        state.recordfn = fn

        rel = client.collection(state.coll.id).get_one(record.id)
        assert len(rel.image) == 3

        r = httpx.get(client.get_file_url(rel, fn, query_params={}))
        assert r.status_code == 200
        assert r.content == bcontent

    def test_remove_file_from_record(self, client: PocketBase, state):
        record = client.collection(state.coll.id).get_one(state.recordid)
        assert len(record.image) == 3
        # delete some of the files from record but keep the file named "state.filename"
        get_record = client.collection(state.coll.id).update(
            record.id, {"image": [state.recordfn]}
        )
        assert record.image != get_record.image
        assert len(get_record.image) == 1

    def test_create_one_file_record(self, client: PocketBase, state):
        name1 = uuid4().hex
        acontent = uuid4().hex
        record = client.collection(state.coll.id).create(
            {
                "title": uuid4().hex,
                "image": FileUpload(name1 + ".txt", acontent, "text/plain"),
            }
        )
        assert len(record.image) == 1
        for fn in record.image:
            assert fn.startswith(name1)

        rel = client.collection(state.coll.id).get_one(record.id)
        assert len(rel.image) == 1

        r = httpx.get(client.get_file_url(rel, rel.image[0], query_params={}))
        assert r.status_code == 200
        assert r.content.decode("utf-8") == acontent

    def test_create_without_file_record2(self, client: PocketBase, state):
        record = client.collection(state.coll.id).create(
            {
                "title": uuid4().hex,
                "image": None,
            }
        )
        assert len(record.image) == 0

        rel = client.collection(state.coll.id).get_one(record.id)
        assert len(rel.image) == 0
