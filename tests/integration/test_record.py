from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError
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
        schema.append(
            {
                "name": "multirel",
                "type": "relation",
                "required": False,
                "options": {
                    "collectionId": state.coll.id,
                    "cascadeDelete": False,
                    "maxSelect": 5,
                },
            },
        )
        state.coll = srv.update(state.coll.id, {"schema": schema})

    def test_create_record(self, client: PocketBase, state):
        bname = uuid4().hex
        state.record = client.collection(state.coll.id).create(
            {
                "title": bname,
            }
        )
        assert state.record.title == bname

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
                    }
                )
                .id
            )

    def test_create_multi_relation_record(self, client: PocketBase, state):
        state.chained_multi_records = [
            state.record.id,
        ]
        for _ in range(4):
            state.chained_multi_records.append(
                client.collection(state.coll.id)
                .create(
                    {
                        "title": uuid4().hex,
                        "multirel": state.chained_multi_records[:],
                    }
                )
                .id
            )

    def test_get_record(self, client: PocketBase, state):
        state.get_record = client.collection(state.coll.id).get_one(state.record.id)
        assert state.get_record.title is not None
        assert state.record.title == state.get_record.title
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

    def test_get_record_expand_multirel(self, client: PocketBase, state):
        rel = client.collection(state.coll.id).get_one(
            state.chained_multi_records[-1],
            {"expand": "multirel.multirel.multirel.multirel"},
        )
        for i, r in enumerate(reversed(state.chained_multi_records)):
            assert rel.id == r
            if i >= 4:
                break
            assert len(rel.expand["multirel"]) == 4 - i
            rel = rel.expand["multirel"][-1]

    def test_get_record_expand_full_list(self, client: PocketBase, state):
        rel = client.collection(state.coll.id).get_full_list(
            query_params={"expand": "rel.rel"}
        )
        i = 0
        for r in rel:
            while r is not None:
                if hasattr(r, "expand"):
                    if "rel" in r.expand:
                        i += 1
                        r = r.expand["rel"]
                        continue
                r = None
        assert i == 19

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

    def test_get_first_list_item(self, client: PocketBase, state):
        return
        items = client.collection(state.coll.id).get_first_list_item(
            'title="%s"' % state.get_record.title
        )
        assert items.title == state.get_record.title

    def test_update_record(self, client: PocketBase, state):
        assert state.record.title == state.get_record.title
        state.get_record = client.collection(state.coll.id).update(
            state.record.id, {"title": uuid4().hex}
        )
        assert state.record.title != state.get_record.title

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
