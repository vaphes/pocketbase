from .connection import get_client_connection
from pocketbase.models.record import Record
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError

from uuid import uuid4
import pytest


def test_crud():
    client = get_client_connection(logged_in_as_master_admin=True)

    email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
    password = uuid4().hex

    srv = client.collection("users")
    created_user = srv.create(
        {
            "email": email,
            "password": password,
            "passwordConfirm": password,
        }
    )
    # should stay logged in as previous admin
    assert isinstance(client.auth_store.model, Admin)
    oldtoken = client.auth_store.token
    srv.auth_with_password(email, password)
    # should now be logged in as new user
    assert isinstance(client.auth_store.model, Record)
    assert client.auth_store.model.id == created_user.id
    # should have gotten a new token
    assert client.auth_store.token != oldtoken
    new_password = uuid4().hex
    srv.update(
        created_user.id,
        {
            "oldPassword": password,
            "password": new_password,
            "passwordConfirm": new_password,
        },
    )
    # Pocketbase will have invalidated the auth token on changing logged-in user
    srv.auth_with_password(email, new_password)
    srv.update(
        created_user.id,
        {
            "username": uuid4().hex,
        },
    )
    srv.delete(created_user.id)


def test_crud_exceptions():
    client = get_client_connection(logged_in_as_master_admin=True)
    srv = client.collection("users")
    with pytest.raises(ClientResponseError) as exc:
        srv.auth_with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400
