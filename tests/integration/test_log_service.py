from pocketbase import PocketBase


class TestLogService:
    def test_log_get_list(self, client: PocketBase, state):
        state.list = client.logs.get_list()

    def test_log_get(self, client: PocketBase, state):
        if len(state.list.items) > 0:
            v = state.list.items[0]
            r = client.logs.get(v.id)
            assert v.id == r.id
            assert v.created == r.created

    def test_log_stats(self, client: PocketBase, state):
        state.stats = client.logs.get_stats()
        assert len(state.stats) >= 0
        for v in state.stats:
            assert v.total > 0
