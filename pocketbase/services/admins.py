from __future__ import annotations

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.services.utils.crud_service import CrudService
from pocketbase.models.admin import Admin


class AdminAuthResponse:
    token: str
    admin: Admin

    def __init__(self, token: str, admin: Admin, **kwargs) -> None:
        self.token = token
        self.admin = admin
        for key, value in kwargs.items():
            setattr(self, key, value)


class Admins(CrudService):
    def decode(self, data: dict) -> BaseModel:
        return Admin(data)

    def base_crud_path(self) -> str:
        return "/api/admins"

    def auth_response(self, response_data: dict) -> AdminAuthResponse:
        """Prepare successful authorize response."""
        admin = self.decode(response_data.pop("admin", {}))
        token = response_data.pop("token", "")
        if token and admin:
            self.client.auth_store.save(token, admin)
        return AdminAuthResponse(token=token, admin=admin, **response_data)

    def auth_via_email(
        self, email: str, password: str, body_params: dict = {}, query_params: dict = {}
    ) -> AdminAuthResponse:
        """
        Authenticate an admin account by its email and password
        and returns a new admin token and data.

        On success this method automatically updates the client's AuthStore data.
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

    def refresh(
        self, body_params: dict = {}, query_params: dict = {}
    ) -> AdminAuthResponse:
        """
        Refreshes the current admin authenticated instance and
        returns a new token and admin data.

        On success this method automatically updates the client's AuthStore data.
        """
        return self.auth_response(
            self.client.send(
                self.base_crud_path() + "/refresh",
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def requestPasswordReset(
        self, email: str, body_params: dict = {}, query_params: dict = {}
    ) -> bool:
        """Sends admin password reset request."""
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

    def confirmPasswordReset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        body_params: dict = {},
        query_params: dict = {},
    ) -> AdminAuthResponse:
        """Confirms admin password reset request."""
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
