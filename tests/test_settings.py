from .connection import client, state, PocketBase

__all__ = ("client", "state")

import pytest
from pocketbase.utils import ClientResponseError
from uuid import uuid4


class TestSettingsService:
    def test_write_setting(self, client: PocketBase, state):
        state.appname = uuid4().hex
        client.settings.update(
            {
                "meta": {
                    "appName": state.appname,
                },
            }
        )

    def test_read_all(self, client: PocketBase, state):
        settings = client.settings.get_all()
        assert state.appname == settings["meta"]["appName"]

    def test_email(self, client: PocketBase, state):
        with pytest.raises(ClientResponseError) as exc:
            client.settings.test_email("", "")
        assert exc.value.status == 400

    def test_s3(self, client: PocketBase, state):
        with pytest.raises(ClientResponseError) as exc:
            client.settings.test_s3()
        assert exc.value.status == 400
