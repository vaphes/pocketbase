from pocketbase import PocketBase  # Client also works the same
from pocketbase.utils import ClientResponseError
import pytest


def get_client_connection(logged_in_as_master_admin: bool = True) -> PocketBase:
    try:
        client = PocketBase("http://127.0.0.1:8090")
        cred = {
            "email": "68e82c0b58bd4ac0@8e8b3687496517e7.com",
            "password": "2f199a97ac9e42e3b9e59b9d939b6e5f",
            "passwordConfirm": "2f199a97ac9e42e3b9e59b9d939b6e5f",
            "avatar": 8,
        }
        try:
            client.admins.create(cred)
        except ClientResponseError:
            pass
        if logged_in_as_master_admin:
            client.admins.auth_with_password(cred["email"], cred["password"])
        return client
    except Exception:
        pytest.skip("No Database found on 127.0.0.1:8090")


def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
