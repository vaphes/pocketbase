from .connection import client, state

__all__ = ("client", "state")
from pocketbase.models.record import Record
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError

from uuid import uuid4
import pytest


class TestRecordAuthService:
    def test_create_user(self, client, state):
        state.email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        state.password = uuid4().hex

        state.srv = client.collection("users")
        state.user = state.srv.create(
            {
                "email": state.email,
                "password": state.password,
                "passwordConfirm": state.password,
            }
        )
        # should stay logged in as previous admin
        assert isinstance(client.auth_store.model, Admin)

    def test_login_user(self, client, state):
        oldtoken = client.auth_store.token
        state.srv.auth_with_password(state.email, state.password)
        # should now be logged in as new user
        assert isinstance(client.auth_store.model, Record)
        assert client.auth_store.model.id == state.user.id
        # should have gotten a new token
        assert client.auth_store.token != oldtoken

    def test_change_password(self, state):
        new_password = uuid4().hex
        state.srv.update(
            state.user.id,
            {
                "oldPassword": state.password,
                "password": new_password,
                "passwordConfirm": new_password,
            },
        )
        # Pocketbase will have invalidated the auth token on changing logged-in user
        state.srv.auth_with_password(state.email, new_password)

    def test_change_username(self, state):
        state.srv.update(state.user.id, {"username": uuid4().hex})

    def test_delete_user(self, state):
        state.srv.delete(state.user.id)


def test_invalid_login_exception(client):
    srv = client.collection("users")
    with pytest.raises(ClientResponseError) as exc:
        srv.auth_with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400
