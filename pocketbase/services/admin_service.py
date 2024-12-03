from __future__ import annotations

from typing import Any

from pocketbase.models.admin import Admin
from pocketbase.services.utils.crud_service import CrudService
from pocketbase.utils import validate_token


class AdminAuthResponse:
    token: str
    admin: Admin

    def __init__(self, token: str, admin: Admin, **kwargs: Any) -> None:
        self.token = token
        self.admin = admin
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_valid(self) -> bool:
        return validate_token(self.token)


class AdminService(CrudService[Admin]):
    def decode(self, data: dict[str, Any]) -> Admin:
        return Admin(data)

    def base_crud_path(self) -> str:
        return "/api/collections/_superusers"

    def update(
        self,
        id: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> Admin:
        """
        If the current `client.auth_store.model` matches with the updated id,
        then on success the `client.auth_store.model` will be updated with the result.
        """
        item = super().update(
            id, body_params=body_params, query_params=query_params
        )
        model = self.client.auth_store.model
        if not isinstance(model, Admin):
            return item
        if item.id == model.id:
            self.client.auth_store.save(self.client.auth_store.token, item)
        return item

    def delete(
        self, id: str, query_params: dict[str, Any] | None = None
    ) -> bool:
        """
        If the current `client.auth_store.model` matches with the deleted id,
        then on success the `client.auth_store` will be cleared.
        """
        success = super().delete(id, query_params=query_params)
        model = self.client.auth_store.model
        if not isinstance(model, Admin):
            return success
        if success:
            self.client.auth_store.clear()
        return success

    def auth_response(self, response_data: dict[str, Any]) -> AdminAuthResponse:
        """Prepare successful authorize response."""
        admin = self.decode(response_data.pop("admin", {}))
        token = response_data.pop("token", "")
        if token and admin:
            self.client.auth_store.save(token, admin)
        return AdminAuthResponse(token=token, admin=admin, **response_data)

    def auth_with_password(
        self,
        email: str,
        password: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> AdminAuthResponse:
        """
        Authenticate an admin account with its email and password
        and returns a new admin token and data.

        On success this method automatically updates the client's AuthStore data.
        """
        body_params = body_params or {}
        body_params.update({"identity": email, "password": password})
        response_data = self.client.send(
            self.base_crud_path() + "/auth-with-password",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
                "headers": {"Authorization": ""},
            },
        )
        return self.auth_response(response_data)

    def auth_refresh(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> AdminAuthResponse:
        """
        Refreshes the current admin authenticated instance and
        returns a new token and admin data.

        On success this method automatically updates the client's AuthStore data.
        """
        return self.auth_response(
            self.client.send(
                self.base_crud_path() + "/auth-refresh",
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def request_password_reset(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """Sends admin password reset request."""
        body_params = body_params or {}
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
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """Confirms admin password reset request."""
        body_params = body_params or {}
        body_params.update(
            {
                "token": password_reset_token,
                "password": password,
                "passwordConfirm": password_confirm,
            }
        )
        self.client.send(
            self.base_crud_path() + "/confirm-password-reset",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    # TODO: add deprecated decorator
    def authRefresh(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> AdminAuthResponse:
        """
        Deprecated: Use `auth_refresh` instead.
        """
        return self.auth_refresh(
            body_params=body_params, query_params=query_params
        )

    # TODO: add deprecated decorator
    def requestPasswordReset(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Deprecated: Use `request_password_reset` instead.
        """
        return self.request_password_reset(
            email, body_params=body_params, query_params=query_params
        )

    # TODO: add deprecated decorator
    def confirmPasswordReset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Deprecated: Use `confirm_password_reset` instead.
        """
        return self.confirm_password_reset(
            password_reset_token,
            password,
            password_confirm,
            body_params=body_params,
            query_params=query_params,
        )
