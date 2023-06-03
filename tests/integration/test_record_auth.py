from pocketbase import PocketBase
from pocketbase.models.record import Record
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError

from uuid import uuid4
import pytest
from time import sleep
from os import environ, path


class TestRecordAuthService:
    def test_create_user(self, client: PocketBase, state):
        state.email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        state.password = uuid4().hex
        state.user = client.collection("users").create(
            {
                "email": state.email,
                "password": state.password,
                "passwordConfirm": state.password,
                "verified": False,
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

    def test_auth_refresh(self, client):
        client.collection("users").authRefresh()

    def test_confirm_email(self, client: PocketBase, state):
        # new_email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        print(state.email)
        sleep(0.2)
        assert client.collection("users").requestVerification(state.email)
        sleep(0.2)
        mail = environ.get("TMP_EMAIL_DIR") + f"/{state.email}"
        assert path.exists(mail)
        print("START")
        for line in open(mail).readlines():
            print(line)
            if "/confirm-verification/" in line:
                token = line.split("/confirm-verification/", 1)[1].split('"')[0]
        assert len(token) > 10
        assert client.collection("users").confirmVerification(token)

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
        state.password = new_password

    def test_change_email(self, client: PocketBase, state):
        new_email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
        assert client.collection("users").requestEmailChange(new_email)
        sleep(0.1)
        mail = environ.get("TMP_EMAIL_DIR") + f"/{new_email}"
        assert path.exists(mail)
        for line in open(mail).readlines():
            if "/confirm-email-change/" in line:
                token = line.split("/confirm-email-change/", 1)[1].split('"')[0]
        assert len(token) > 10
        assert client.collection("users").confirmEmailChange(token, state.password)
        client.collection("users").auth_with_password(new_email, state.password)
        state.email = new_email

    def test_request_password_reset(self, client: PocketBase, state):
        client.auth_store.clear()
        state.password = uuid4().hex
        assert client.collection("users").requestPasswordReset(state.email)
        sleep(0.1)
        mail = environ.get("TMP_EMAIL_DIR") + f"/{state.email}"
        assert path.exists(mail)
        for line in open(mail).readlines():
            if "/confirm-password-reset/" in line:
                token = line.split("/confirm-password-reset/", 1)[1].split('"')[0]
        assert len(token) > 10
        assert client.collection("users").confirmPasswordReset(
            token, state.password, state.password
        )
        client.collection("users").auth_with_password(state.email, state.password)

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
