import pytest
import os

from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError


class State:
    def __init__(self):
        pass


@pytest.fixture(scope="class")
def state() -> State:
    return State()


@pytest.fixture(scope="class")
def client() -> PocketBase:
    try:
        url = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")
        email = os.getenv(
            "POCKETBASE_TEST_EMAIL", "68e82c0b58bd4ac0@8e8b3687496517e7.com"
        )
        password = os.getenv(
            "POCKETBASE_TEST_PASSWORD", "2f199a97ac9e42e3b9e59b9d939b6e5f"
        )
        client = PocketBase(url)
        cred = {
            "email": email,
            "password": password,
            "passwordConfirm": password,
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
