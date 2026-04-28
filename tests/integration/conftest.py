import pytest
from environs import env

from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError

env.read_env()


class State:
    def __init__(self):
        pass


@pytest.fixture(scope="class")
def state() -> State:
    return State()


@pytest.fixture(scope="class")
def client() -> PocketBase:
    try:
        url = env.str("POCKETBASE_URL", "http://127.0.0.1:8090")
        email = env.str(
            "POCKETBASE_TEST_EMAIL", "68e82c0b58bd4ac0@8e8b3687496517e7.com"
        )
        password = env.str(
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
            client.collection("_superusers").create(cred)
        except ClientResponseError:
            pass
        client.collection("_superusers").auth_with_password(
            str(cred["email"]), str(cred["password"])
        )
        return client
    except Exception:
        pytest.skip("No Database found on 127.0.0.1:8090")
