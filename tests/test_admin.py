from .connection import client, state, PocketBase

__all__ = ("client", "state")
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError
from uuid import uuid4
import pytest


class TestAdminService:
    def test_login(self, client: PocketBase):
        assert isinstance(client.auth_store.model, Admin)

    def test_create_admin(self, client: PocketBase, state):
        state.email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        state.password = uuid4().hex
        state.admin = client.admins.create(
            {
                "email": state.email,
                "password": state.password,
                "passwordConfirm": state.password,
                "avatar": 8,
            }
        )
        # should stay logged in as previous admin
        assert client.auth_store.model.id != state.admin.id

    def test_login_as_created_admin(self, client: PocketBase, state):
        client.admins.auth_with_password(state.email, state.password)
        assert client.auth_store.model.id == state.admin.id

    def test_update_admin(self, client: PocketBase, state):
        new_email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        new_password = uuid4().hex
        client.admins.update(
            state.admin.id,
            {
                "email": new_email,
                "password": new_password,
                "passwordConfirm": new_password,
                "avatar": 8,
            },
        )
        # Pocketbase will have invalidated the auth token on changing logged-in user
        client.admins.auth_with_password(new_email, new_password)

    def test_delete_admin(self, client: PocketBase, state):
        client.admins.delete(state.admin.id)


def test_invalid_login_exception(client):
    with pytest.raises(ClientResponseError) as exc:
        client.admins.auth_with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400  # invalid login


def test_connection_error_exception():
    client = PocketBase("http://127.0.0.2:9090")
    with pytest.raises(ClientResponseError) as exc:
        client.admins.auth_with_password(uuid4().hex, uuid4().hex)
    assert isinstance(exc.value, ClientResponseError)


def test_auth_refresh(client):
    oldid = client.auth_store.model.id
    ar = client.admins.authRefresh()
    assert client.auth_store.token == ar.token
    assert client.auth_store.model.id == oldid
