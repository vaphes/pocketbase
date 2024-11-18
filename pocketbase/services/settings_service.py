from __future__ import annotations

from typing import Any

from pocketbase.services.utils.base_service import BaseService


class SettingsService(BaseService):
    def get_all(
        self, query_params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Fetch all available app settings."""
        return self.client.send(
            "/api/settings",
            {"method": "GET", "params": query_params},
        )

    def update(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Bulk updates app settings."""
        return self.client.send(
            "/api/settings",
            {
                "method": "PATCH",
                "params": query_params,
                "body": body_params,
            },
        )

    def test_s3(self, query_params: dict[str, Any] | None = None) -> bool:
        """Performs a S3 storage connection test."""
        self.client.send(
            "/api/settings/test/s3",
            {"method": "POST", "params": query_params},
        )
        return True

    def test_email(
        self,
        to_email: str,
        email_template: str,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Sends a test email.

        The possible `email_template` values are:
        - verification
        - password-reset
        - email-change
        """
        self.client.send(
            "/api/settings/test/email",
            {
                "method": "POST",
                "params": query_params,
                "body": {"email": to_email, "template": email_template},
            },
        )
        return True

    def generate_apple_client_secret(
        self,
        client_id: str,
        team_id: str,
        key_id: str,
        private_key: str,
        duration: int,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        res = self.client.send(
            "/api/settings/apple/generate-client-secret",
            {
                "method": "POST",
                "params": query_params,
                "body": {
                    "clientId": client_id,
                    "teamId": team_id,
                    "keyId": key_id,
                    "privateKey": private_key,
                    "duration": duration,
                },
            },
        )
        return res.get("secret")
