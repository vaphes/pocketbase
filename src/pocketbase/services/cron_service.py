from dataclasses import dataclass

from pocketbase.services.base_service import BaseService


@dataclass
class CronJob:
    id: str
    expression: str


class CronService(BaseService):
    def get_full_list(self, query_params: dict | None = None) -> list[CronJob]:
        """Returns list with all registered cron jobs."""
        result = self.client.send(
            "/api/crons",
            {
                "method": "GET",
                "params": query_params,
            },
        )
        return [CronJob(**item) for item in result]

    def run(self, job_id: str, query_params: dict | None = None) -> bool:
        """Runs the specified cron job."""
        self.client.send(
            f"/api/crons/{job_id}",
            {
                "method": "POST",
                "params": query_params,
            },
        )
        return True
