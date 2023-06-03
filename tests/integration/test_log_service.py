from pocketbase import PocketBase


class TestLogService:
    def test_get_request_list(self, client: PocketBase, state):
        state.list = client.logs.get_request_list()

    def test_get_request(self, client: PocketBase, state):
        if len(state.list.items) > 0:
            v = state.list.items[0]
            r = client.logs.get_request(v.id)
            assert v.id == r.id
            assert v.created == r.created

    def test_log_request_stats(self, client: PocketBase, state):
        state.stats = client.logs.get_requests_stats()
        assert len(state.stats) > 0
        for v in state.stats:
            assert v.total > 0
