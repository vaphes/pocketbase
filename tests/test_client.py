from pytest_httpx import HTTPXMock
import httpx
from pocketbase import PocketBase


def test_custom_headers(httpx_mock: HTTPXMock):
    # return empty json as response
    httpx_mock.add_response(json={})

    with httpx.Client(headers={"key": "value"}) as http_client:
        client = PocketBase("http://testclient", http_client=http_client)
        _ = client.collection("users").get_list()
        request = httpx_mock.get_request()
        assert request.headers["key"] == "value"
