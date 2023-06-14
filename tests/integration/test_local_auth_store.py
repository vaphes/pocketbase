from pocketbase import PocketBase
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError
from pocketbase.stores.local_auth_store import LocalAuthStore
from uuid import uuid4
import pytest
import tempfile


class TestLocalAuthStore:
    def test_save(self, state):
        state.tmp = tempfile.mkdtemp()
        state.token = uuid4().hex
        state.admin = Admin(
            {
                "id": "38wgsiz3pdsu1j7",
                "avatar": 8,
                "email": "68e82c0b58bd4ac0@8e8b3687496517e7.com",
            }
        )
        store = LocalAuthStore(filepath=state.tmp)
        store.save(state.token, state.admin)

    def test_load(self, state):
        store = LocalAuthStore(filepath=state.tmp)
        assert store.token == state.token
        assert store.model.email == state.admin.email

    def test_clear(self, state):
        store = LocalAuthStore(filepath=state.tmp)
        store.clear()
        assert store.token != state.token
        assert store.model is None


def test_invalid_login_exception(client):
    with pytest.raises(ClientResponseError) as exc:
        client.admins.auth_with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400  # invalid login


def test_local_store_integration(client):
    tmp = tempfile.mkdtemp()
    l_store = LocalAuthStore(filepath=tmp)
    la_client = PocketBase(client.base_url, auth_store=l_store)
    with pytest.raises(ClientResponseError):
        la_client.admins.authRefresh()
    la_client.auth_store.save(client.auth_store.token, client.auth_store.model)
    la_client.admins.authRefresh()
