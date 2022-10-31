from __future__ import annotations

from pocketbase.services.utils.base_service import BaseService


class SettingsService(BaseService):
    def get_all(self, query_params: dict = {}) -> dict:
        """Fetch all available app settings."""
        return self.client.send(
            "/api/settings",
            {"method": "GET", "params": query_params},
        )

    def update(self, body_params: dict = {}, query_params: dict = {}) -> dict:
        """Bulk updates app settings."""
        return self.client.send(
            "/api/settings",
            {
                "method": "PATCH",
                "params": query_params,
                "body": body_params,
            },
        )

    def test_s3(self, query_params: dict = {}) -> bool:
        """Performs a S3 storage connection test."""
        self.client.send(
            "/api/settings/test/s3",
            {"method": "POST", "params": query_params},
        )
        return True

    def test_email(
        self, to_email: str, email_template: str, query_params: dict = {}
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
