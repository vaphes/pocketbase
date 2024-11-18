from uuid import uuid4

from pocketbase import PocketBase
from pocketbase.services.health_service import HealthCheckResponse


class TestHealthService:
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
        state.coll = srv.update(state.coll.id, {"schema": schema})

    def test_check(self, client: PocketBase, state):
        ret = client.health.check()
        assert isinstance(ret, HealthCheckResponse)
        assert ret.code == 200
