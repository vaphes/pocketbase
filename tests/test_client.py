from pytest_httpx import HTTPXMock

from pocketbase import PocketBase


def test_custom_headers(httpx_mock: HTTPXMock):
    # return empty json as response
    httpx_mock.add_response(json={})

    client = PocketBase("http://testclient")
    _ = client.collection("users").get_list()
    request = httpx_mock.get_request()
    assert request is not None
