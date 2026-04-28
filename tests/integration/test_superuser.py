from os import path
from time import sleep
from uuid import uuid4

import pytest
from environs import env

from pocketbase import PocketBase
from pocketbase.models.record import Record
from pocketbase.utils import ClientResponseError


class TestSuperuserService:
    def test_login(self, client: PocketBase):
        assert isinstance(client.auth_store.model, Record)

    def test_create_superuser(self, client: PocketBase, state):
        state.email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        state.password = uuid4().hex
        state.admin = client.collection("_superusers").create(
            {
                "email": state.email,
                "password": state.password,
                "passwordConfirm": state.password,
                "avatar": 8,
            }
        )
        # should stay logged in as previous admin
        assert client.auth_store.model is not None
        assert client.auth_store.model.id != state.admin.id

    def test_login_as_created_superuser(self, client: PocketBase, state):
        client.collection("_superusers").auth_with_password(
            state.email, state.password
        )
        assert client.auth_store.model is not None
        assert client.auth_store.model.id == state.admin.id

    def test_update_superuser(self, client: PocketBase, state):
        state.new_email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        new_password = uuid4().hex
        client.collection("_superusers").update(
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
        client.collection("_superusers").auth_with_password(
            state.new_email, new_password
        )

    def test_superuser_password_reset(self, client: PocketBase, state):
        assert client.collection("_superusers").request_password_reset(
            state.new_email
        )
        sleep(0.1)
        mail = env.str("TMP_EMAIL_DIR", "") + f"/{state.new_email}"
        assert path.exists(mail)
        for line in open(mail).readlines():
            if "/confirm-password-reset/" in line:
                token = line.split("/confirm-password-reset/", 1)[1].split('"')[
                    0
                ]
        assert len(token) > 10
        new_password = uuid4().hex
        assert client.collection("_superusers").confirm_password_reset(
            token, new_password, new_password
        )
        client.collection("_superusers").auth_with_password(
            state.new_email, new_password
        )

    def test_delete_superuser(self, client: PocketBase, state):
        client.collection("_superusers").delete(state.admin.id, query_params={})


def test_invalid_login_exception(client):
    with pytest.raises(ClientResponseError) as exc:
        client.collection("_superusers").auth_with_password(
            uuid4().hex, uuid4().hex
        )
    assert exc.value.status == 400  # invalid login


def test_connection_error_exception():
    client = PocketBase("http://127.0.0.2:9090", timeout=1)
    with pytest.raises(ClientResponseError) as exc:
        client.collection("_superusers").auth_with_password(
            uuid4().hex, uuid4().hex
        )
    assert isinstance(exc.value, ClientResponseError)


def test_auth_refresh(client):
    oldid = client.auth_store.model.id
    ar = client.collection("_superusers").auth_refresh()
    assert client.auth_store.token == ar.token
    assert client.auth_store.model.id == oldid
