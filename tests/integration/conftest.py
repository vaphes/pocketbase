from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError
import pytest


class State:
    def __init__(self):
        pass


@pytest.fixture(scope="class")
def state() -> State:
    return State()


@pytest.fixture(scope="class")
def client() -> PocketBase:
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
        client.admins.auth_with_password(cred["email"], cred["password"])
        return client
    except Exception:
        pytest.skip("No Database found on 127.0.0.1:8090")
