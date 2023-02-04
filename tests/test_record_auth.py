from .connection import client, state, PocketBase

__all__ = ("client", "state")
from pocketbase.models.record import Record
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError

from uuid import uuid4
import pytest


class TestRecordAuthService:
    def test_create_user(self, client: PocketBase, state):
        state.email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        state.password = uuid4().hex
        state.user = client.collection("users").create(
            {
                "email": state.email,
                "password": state.password,
                "passwordConfirm": state.password,
            }
        )
        # should stay logged in as previous admin
        assert isinstance(client.auth_store.model, Admin)

    def test_login_user(self, client: PocketBase, state):
        oldtoken = client.auth_store.token
        client.auth_store.clear()
        client.collection("users").auth_with_password(state.email, state.password)
        # should now be logged in as new user
        assert isinstance(client.auth_store.model, Record)
        assert client.auth_store.model.id == state.user.id
        # should have gotten a new token
        assert client.auth_store.token != oldtoken

    def test_change_password(self, client: PocketBase, state):
        new_password = uuid4().hex
        client.collection("users").update(
            state.user.id,
            {
                "oldPassword": state.password,
                "password": new_password,
                "passwordConfirm": new_password,
            },
        )
        # Pocketbase will have invalidated the auth token on changing logged-in user
        client.collection("users").auth_with_password(state.email, new_password)

    def test_change_username(self, client: PocketBase, state):
        client.collection("users").update(state.user.id, {"username": uuid4().hex})

    def test_delete_user(self, client: PocketBase, state):
        client.collection("users").delete(state.user.id)


def test_invalid_login_exception(client):
    with pytest.raises(ClientResponseError) as exc:
        client.collection("users").auth_with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400


def test_list_auth_methods(client):
    val = client.collection("users").list_auth_methods()
    assert isinstance(val.username_password, bool)
    assert isinstance(val.email_password, bool)
    assert isinstance(val.auth_providers, list)
