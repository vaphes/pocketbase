from pocketbase import PocketBase
from uuid import uuid4
from pocketbase.services import RecordService
from pocketbase.services.realtime_service import MessageData
from pocketbase.models import Record

from time import sleep


class TestRecordEventService:
    def test_init_collection(self, client: PocketBase, state):
        # create collection
        schema = [
            {
                "name": "title",
                "type": "text",
                "required": True,
            },
        ]
        state.coll = client.collections.create(
            {
                "name": uuid4().hex,
                "type": "base",
                "schema": schema,
            }
        )
        state.c: RecordService = client.collection(state.coll.id)

    def test_subscribe_event(self, client: PocketBase, state):
        c: RecordService = state.c
        state.test_subscribe_event = None

        def callback(e: MessageData):
            state.test_subscribe_event = e

        c.subscribe(callback)
        sleep(0.1)
        for _ in range(2):
            state.record = state.c.create({"title": uuid4().hex})
            sleep(0.1)
            e: MessageData = state.test_subscribe_event
            assert e.record.collection_id == state.coll.id
            assert e.record.id == state.record.id
        c.unsubscribe()
        c.unsubscribe()
        client.realtime.unsubscribe([])
        sleep(0.1)
        for _ in range(2):
            state.c.create({"title": uuid4().hex})
            sleep(0.1)
            # e should now not be mutated any more as we are unsubscribed
            e: MessageData = state.test_subscribe_event
            assert e.record.collection_id == state.coll.id
            assert e.record.id == state.record.id

    def test_subscribe_single_record(self, client: PocketBase, state):
        c: RecordService = state.c
        r: Record = state.record
        state.test_subscribe_event2 = None

        def callback_ex(e: MessageData):
            raise Exception("This Callback should be never called")

        def callback(e: MessageData):
            state.test_subscribe_event2 = e

        c.subscribeOne(r.id, callback_ex)
        # subscribing a second time should erase first subscription (for code coverage)
        c.subscribeOne(r.id, callback)
        sleep(0.1)
        for _ in range(2):
            r = c.update(r.id, {"title": uuid4().hex})
            sleep(0.1)
            e: MessageData = state.test_subscribe_event2
            assert e.record.collection_id == state.coll.id
            assert e.record.id == r.id
            state.test_subscribe_event2.record.id = "abc"
        c.unsubscribe(r.id, r.id)
        sleep(0.1)

        for _ in range(2):
            c.update(r.id, {"title": uuid4().hex})
            sleep(0.1)
            # e should now not be mutated any more as we are unsubscribed
            e: MessageData = state.test_subscribe_event2
            assert e.record.collection_id == state.coll.id
            assert e.record.id == "abc"
