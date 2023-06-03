from pocketbase import PocketBase
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError
from uuid import uuid4
import pytest
from os import environ, path
from time import sleep


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
        state.new_email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        new_password = uuid4().hex
        client.admins.update(
            state.admin.id,
            {
                "email": state.new_email,
                "password": new_password,
                "passwordConfirm": new_password,
                "avatar": 8,
            },
            query_params={},
        )
        # Pocketbase will have invalidated the auth token on changing logged-in user
        client.admins.auth_with_password(state.new_email, new_password)

    def test_admin_password_reset(self, client: PocketBase, state):
        assert client.admins.requestPasswordReset(state.new_email)
        sleep(0.1)
        mail = environ.get("TMP_EMAIL_DIR") + f"/{state.new_email}"
        assert path.exists(mail)
        for line in open(mail).readlines():
            if "/confirm-password-reset/" in line:
                token = line.split("/confirm-password-reset/", 1)[1].split('"')[0]
        assert len(token) > 10
        new_password = uuid4().hex
        assert client.admins.confirmPasswordReset(token, new_password, new_password)
        client.admins.auth_with_password(state.new_email, new_password)

    def test_delete_admin(self, client: PocketBase, state):
        client.admins.delete(state.admin.id, query_params={})


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
