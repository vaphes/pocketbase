from .connection import get_client_connection
from pocketbase.models.admin import Admin
from pocketbase.utils import ClientResponseError

from uuid import uuid4
import pytest


def test_crud():
    client = get_client_connection(logged_in_as_master_admin=True)
    assert isinstance(client.auth_store.model, Admin)
    email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
    password = uuid4().hex

    def record(email, password):
        return {
            "email": email,
            "password": password,
            "passwordConfirm": password,
            "avatar": 8,
        }

    created_admin = client.admins.create(record(email, password))
    # should stay logged in as previous admin
    assert client.auth_store.model.id != created_admin.id
    client.admins.auth_with_password(email, password)
    # should now be logged in as new admin
    assert client.auth_store.model.id == created_admin.id

    new_email = "%s@%s.com" % (uuid4().hex[:16], uuid4().hex[:16])
    new_password = uuid4().hex
    client.admins.update(created_admin.id, record(new_email, new_password))
    # Pocketbase will have invalidated the auth token on changing logged-in user
    client.admins.auth_with_password(new_email, new_password)
    client.admins.delete(created_admin.id)


def test_crud_exceptions():
    client = get_client_connection(logged_in_as_master_admin=True)
    with pytest.raises(ClientResponseError) as exc:
        client.admins.auth_with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400
