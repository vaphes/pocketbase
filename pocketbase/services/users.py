from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote
from pocketbase.services.utils.crud_service import CrudService
from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.user import User
from pocketbase.models.external_auth import ExternalAuth


class UserAuthResponse:
    token: str
    user: User

    def __init__(self, token: str, user: User, **kwargs) -> None:
        self.token = token
        self.user = user
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
    email_password: bool
    auth_providers: list[AuthProviderInfo]


class Users(CrudService):
    def decode(self, data: dict) -> BaseModel:
        return User(data)

    def base_crud_path(self) -> str:
        return "/api/users"

    def auth_response(self, response_data: Any) -> UserAuthResponse:
        """Prepare successful authorization response."""
        user = self.decode(response_data.pop("user", {}))
        token = response_data.pop("token", "")
        if token and user:
            self.client.auth_store.save(token, user)
        return UserAuthResponse(token=token, user=user, **response_data)

    def list_auth_methods(self, query_params: dict = {}) -> AuthMethodsList:
        """Returns all available application auth methods."""
        response_data = self.client.send(
            self.base_crud_path() + "/auth-methods",
            {"method": "GET", "params": query_params},
        )
        email_password = response_data.get("emailPassword", False)
        auth_providers = [
            AuthProviderInfo(auth_provider)
            for auth_provider in response_data.get("authProviders", [])
        ]
        return AuthMethodsList(email_password, auth_providers)

    def auth_via_email(
        self, email: str, password: str, body_params: dict = {}, query_params: dict = {}
    ) -> UserAuthResponse:
        """
        Authenticate a user via its email and password.

        On success, this method also automatically updates
        the client's AuthStore data and returns:
        - new user authentication token
        - the authenticated user model record
        """
        body_params.update({"email": email, "password": password})
        response_data = self.client.send(
            self.base_crud_path() + "/auth-via-email",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
                "headers": {"Authorization": ""},
            },
        )
        return self.auth_response(response_data)

    def auth_via_oauth2(
        self,
        provider: str,
        code: str,
        code_verifier: str,
        redirect_url: str,
        body_params: dict = {},
        query_params: dict = {},
    ) -> UserAuthResponse:
        """
        Authenticate a user via OAuth2 client provider.

        On success, this method also automatically updates
        the client's AuthStore data and returns:
        - new user authentication token
        - the authenticated user model record
        - the OAuth2 user profile data (eg. name, email, avatar, etc.)
        """
        body_params.update(
            {
                "provider": provider,
                "code": code,
                "codeVerifier": code_verifier,
                "redirectUrl": redirect_url,
            }
        )
        response_data = self.client.send(
            self.base_crud_path() + "/auth-via-oauth2",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
                "headers": {"Authorization": ""},
            },
        )
        return self.auth_response(response_data)

    def refresh(
        self, body_params: dict = {}, query_params: dict = {}
    ) -> UserAuthResponse:
        """
        Refreshes the current user authenticated instance and
        returns a new token and user data.

        On success this method also automatically updates the client's AuthStore data.
        """
        return self.auth_response(
            self.client.send(
                self.base_crud_path() + "/refresh",
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def request_password_reset(
        self, email: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Sends user password reset request."""
        body_params.update({"email": email})
        self.client.send(
            self.base_crud_path() + "/request-password-reset",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirm_password_reset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        body_params: dict = {},
        query_params: dict = {},
    ) -> UserAuthResponse:
        """Confirms user password reset request."""
        body_params.update(
            {
                "token": password_reset_token,
                "password": password,
                "passwordConfirm": password_confirm,
            }
        )
        return self.auth_response(
            self.client.send(
                self.base_crud_path() + "/confirm-password-reset",
                {
                    "method": "POST",
                    "params": query_params,
                    "body": body_params,
                },
            )
        )

    def request_verification(
        self, email: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Sends user verification email request."""
        body_params.update({"email": email})
        self.client.send(
            self.base_crud_path() + "/request-verification",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirm_verification(
        self, verification_token: str, body_params: dict = {}, query_params: dict = {}
    ) -> UserAuthResponse:
        """Confirms user email verification request."""
        body_params.update(
            {
                "token": verification_token,
            }
        )
        return self.auth_response(
            self.client.send(
                self.base_crud_path() + "/confirm-verification",
                {
                    "method": "POST",
                    "params": query_params,
                    "body": body_params,
                },
            )
        )

    def request_email_change(
        self, new_email: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Sends an email change request to the authenticated user."""
        body_params.update({"newEmail": new_email})
        self.client.send(
            self.base_crud_path() + "/request-email-change",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirm_email_change(
        self,
        email_change_token: str,
        password: str,
        body_params: dict = {},
        query_params: dict = {},
    ) -> UserAuthResponse:
        """Confirms user new email address."""
        body_params.update(
            {
                "token": email_change_token,
                "password": password,
            }
        )
        return self.auth_response(
            self.client.send(
                self.base_crud_path() + "/confirm-email-change",
                {
                    "method": "POST",
                    "params": query_params,
                    "body": body_params,
                },
            )
        )

    def list_external_auths(
        self, user_id: str, query_params: dict = {}
    ) -> list[ExternalAuth]:
        """Lists all linked external auth providers for the specified user."""
        response_data = self.client.send(
            self.base_crud_path() + "/" + quote(user_id) + "/external-auths",
            {"method": "GET", "params": query_params},
        )
        return [ExternalAuth(item) for item in response_data]

    def unlink_external_auth(
        self, user_id: str, provider: str, query_params: dict = {}
    ) -> bool:
        """Unlink a single external auth provider from the specified user."""
        self.client.send(
            self.base_crud_path()
            + "/"
            + quote(user_id)
            + "/external-auths/"
            + quote(provider),
            {"method": "DELETE", "params": query_params},
        )
        return True
