from pocketbase import PocketBase
import pytest
from pocketbase.utils import ClientResponseError
from uuid import uuid4
from os import environ, path


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
        addr = uuid4().hex
        assert client.settings.test_email(f"settings@{addr}.com", "verification")
        assert path.exists(environ.get("TMP_EMAIL_DIR") + f"/settings@{addr}.com")

    def test_s3(self, client: PocketBase, state):
        with pytest.raises(ClientResponseError) as exc:
            client.settings.test_s3()
        assert exc.value.status == 400
