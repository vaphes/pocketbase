from __future__ import annotations
from dataclasses import dataclass
from typing import List

from urllib.parse import quote, urlencode
from pocketbase.services.realtime_service import Callable, MessageData

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.record import Record
from pocketbase.services.utils.crud_service import CrudService
from pocketbase.utils import camel_to_snake


class RecordAuthResponse:
    token: str
    record: Record

    def __init__(self, token: str, record: Record, **kwargs) -> None:
        self.token = token
        self.record = record
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class AuthProviderInfo:
    name: str
    state: str
    code_verifier: str
    code_challenge: str
    code_challenge_method: str
    auth_url: str


@dataclass
class AuthMethodsList:
    username_password: bool
    email_password: bool
    auth_providers: list[AuthProviderInfo]


class RecordService(CrudService):
    collection_id_or_name: str

    def __init__(self, client, collection_id_or_name) -> None:
        super().__init__(client)
        self.collection_id_or_name = collection_id_or_name

    def decode(self, data: dict) -> BaseModel:
        return Record(data)

    def base_crud_path(self) -> str:
        return self.base_collection_path() + "/records"

    def base_collection_path(self) -> str:
        """Returns the current collection service base path."""
        return "/api/collections/" + quote(self.collection_id_or_name)

    def get_file_url(
        self, record: Record, filename: str, query_params: dict = {}
    ) -> str:
        """Builds and returns an absolute record file url."""
        base_url = self.client.base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        result = f"{base_url}/api/files/{record.collection_id}/{record.id}/{filename}"
        if query_params:
            result += "?" + urlencode(query_params)
        return result

    def subscribe(self, callback: Callable[[MessageData], None]):
        """Subscribe to realtime changes of any record from the collection."""
        return self.client.realtime.subscribe(self.collection_id_or_name, callback)

    def subscribeOne(self, record_id: str, callback: Callable[[MessageData], None]):
        """Subscribe to the realtime changes of a single record in the collection."""
        return self.client.realtime.subscribe(
            self.collection_id_or_name + "/" + record_id, callback
        )

    def unsubscribe(self, *record_ids: List[str]):
        """Unsubscribe to the realtime changes of a single record in the collection."""
        if record_ids and len(record_ids) > 0:
            subs = []
            for id in record_ids:
                subs.append(self.collection_id_or_name + "/" + id)
            return self.client.realtime.unsubscribe(subs)
        return self.client.realtime.unsubscribe_by_prefix(self.collection_id_or_name)

    def update(self, id: str, body_params: dict = {}, query_params: dict = {}):
        """
        If the current `client.auth_store.model` matches with the updated id, then
        on success the `client.auth_store.model` will be updated with the result.
        """
        item = super().update(id, body_params=body_params, query_params=query_params)
        try:
            if (
                self.client.auth_store.model.collection_id is not None
                and item.id == self.client.auth_store.model.id
            ):
                self.client.auth_store.save(self.client.auth_store.token, item)
        except:
            pass
        return item

    def delete(self, id: str, query_params: dict = {}):
        """
        If the current `client.auth_store.model` matches with the deleted id,
        then on success the `client.auth_store` will be cleared.
        """
        success = super().delete(id, query_params)
        try:
            if (
                success
                and self.client.auth_store.model.collection_id is not None
                and id == self.client.auth_store.model.id
            ):
                self.client.auth_store.clear()
        except:
            pass
        return success

    def auth_response(self, response_data: dict) -> RecordAuthResponse:
        """Prepare successful collection authorization response."""
        record = self.decode(response_data.pop("record", {}))
        token = response_data.pop("token", "")
        if token and record:
            self.client.auth_store.save(token, record)
        return RecordAuthResponse(token=token, record=record, **response_data)

    def list_auth_methods(self, query_params: str = {}):
        """Returns all available collection auth methods."""
        response_data = self.client.send(
            self.base_collection_path() + "/auth-methods",
            {"method": "GET", "params": query_params},
        )
        username_password = response_data.pop("usernamePassword", False)
        email_password = response_data.pop("emailPassword", False)

        def apply_pythonic_keys(ap):
            pythonic_keys_ap = {
                camel_to_snake(key).replace("@", ""): value for key, value in ap.items()
            }
            return pythonic_keys_ap

        auth_providers = [
            AuthProviderInfo(**auth_provider)
            for auth_provider in map(
                apply_pythonic_keys, response_data.get("authProviders", [])
            )
        ]
        return AuthMethodsList(username_password, email_password, auth_providers)

    def auth_with_password(
        self,
        username_or_email: str,
        password: str,
        body_params: dict = {},
        query_params: dict = {},
    ) -> RecordAuthResponse:
        """
        Authenticate a single auth collection record via its username/email and password.

        On success, this method also automatically updates
        the client's AuthStore data and returns:
        - the authentication token
        - the authenticated record model
        """
        body_params.update({"identity": username_or_email, "password": password})
        response_data = self.client.send(
            self.base_collection_path() + "/auth-with-password",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
                "headers": {"Authorization": ""},
            },
        )
        return self.auth_response(response_data)

    def auth_with_oauth2(
        self,
        provider: str,
        code: str,
        code_verifier: str,
        redirect_url: str,
        create_data={},
        body_params={},
        query_params={},
    ):
        """
        Authenticate a single auth collection record with OAuth2.

        On success, this method also automatically updates
        the client's AuthStore data and returns:
        - the authentication token
        - the authenticated record model
        - the OAuth2 account data (eg. name, email, avatar, etc.)
        """
        body_params.update(
            {
                "provider": provider,
                "code": code,
                "codeVerifier": code_verifier,
                "redirectUrl": redirect_url,
                "createData": create_data,
            }
        )
        response_data = self.client.send(
            self.base_collection_path() + "/auth-with-oauth2",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return self.auth_response(response_data)

    def authRefresh(
        self, body_params: dict = {}, query_params: dict = {}
    ) -> RecordAuthResponse:
        """
        Refreshes the current authenticated record instance and
        returns a new token and record data.

        On success this method also automatically updates the client's AuthStore.
        """
        return self.auth_response(
            self.client.send(
                self.base_collection_path() + "/auth-refresh",
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def requestEmailChange(
        self, newEmail: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """
        Asks to change email of the current authenticated record instance the new address
        receives an email with a confirmation token that needs to be confirmed with confirmEmailChange()
        """
        body_params.update({"newEmail": newEmail})
        self.client.send(
            self.base_collection_path() + "/request-email-change",
            {"method": "POST", "params": query_params, "body": body_params},
        )
        return True

    def confirmEmailChange(
        self, token: str, password: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """
        Confirms Email Change by with the confirmation token and confirm with users password
        """
        body_params.update({"token": token, "password": password})
        self.client.send(
            self.base_collection_path() + "/confirm-email-change",
            {"method": "POST", "params": query_params, "body": body_params},
        )
        return True

    def requestPasswordReset(
        self, email: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Sends auth record password reset request."""
        body_params.update({"email": email})
        self.client.send(
            self.base_collection_path() + "/request-password-reset",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def requestVerification(
        self, email: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Sends email verification request."""
        body_params.update({"email": email})
        self.client.send(
            self.base_collection_path() + "/request-verification",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirmPasswordReset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        body_params: dict = {},
        query_params: dict = {},
    ) -> bool:
        """Confirms auth record password reset request"""
        body_params.update(
            {
                "token": password_reset_token,
                "password": password,
                "passwordConfirm": password_confirm,
            }
        )

        self.client.send(
            self.base_collection_path() + "/confirm-password-reset",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirmVerification(
        self, token: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Confirms email verification request."""
        body_params.update({"token": token})
        self.client.send(
            self.base_collection_path() + "/confirm-verification",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True
