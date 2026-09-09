from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import Settings
from app.domain.models import Opportunity, OpportunityType

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


class AdzunaSourceError(RuntimeError):
    """Raised when the Adzuna API cannot be queried or returns unusable data.

    Any failure here is treated as a hard error, not silently swallowed: it
    is safer to fail a run loudly (see Edge-cases.md) than to interpret a
    rate limit or auth failure as "no more results".
    """


class AdzunaOpportunitySource:
    """Fetches job/internship listings from the Adzuna Job Search API.

    Requires ADZUNA_APP_ID and ADZUNA_APP_KEY (see app/config.py).

    Known limitations, documented rather than silently handled:
    - Adzuna provides no explicit remote flag or application deadline;
      both are left unset (None) rather than guessed from free text.
    - A failure on any page aborts the whole fetch generator. Because
      app/ingestion/service.py only commits once at the end of a full
      run, a mid-run failure rolls back everything ingested so far in
      that run, including earlier pages that succeeded. This is a known
      Phase 2 gap (see documentation/PHASE-2-STATUS.md) tied to the
      missing run-level provenance/retry work, not something this
      adapter can fix on its own.
    """

    name = "adzuna"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            raise AdzunaSourceError(
                "ADZUNA_APP_ID and ADZUNA_APP_KEY must be configured to use this source"
            )
        self._settings = settings
        self._client = client

    async def fetch(self) -> AsyncIterator[Opportunity]:
        async with self._client_context() as client:
            for page in range(1, self._settings.adzuna_max_pages + 1):
                jobs = await self._fetch_page(client, page=page)
                if not jobs:
                    return
                for job in jobs:
                    opportunity = self._to_opportunity(job)
                    if opportunity is not None:
                        yield opportunity

    async def health_check(self) -> bool:
        try:
            async with self._client_context() as client:
                await self._fetch_page(client, page=1, results_per_page=1)
            return True
        except AdzunaSourceError:
            return False

    def _client_context(self) -> httpx.AsyncClient:
        return self._client or httpx.AsyncClient(timeout=10.0)

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        page: int,
        results_per_page: int | None = None,
    ) -> list[dict[str, Any]]:
        url = f"{ADZUNA_BASE_URL}/{self._settings.adzuna_country}/search/{page}"
        params = {
            "app_id": self._settings.adzuna_app_id,
            "app_key": self._settings.adzuna_app_key,
            "results_per_page": results_per_page or self._settings.adzuna_results_per_page,
            "what": self._settings.adzuna_what,
            "content-type": "application/json",
        }
        try:
            response = await client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise AdzunaSourceError(f"Adzuna request timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            raise AdzunaSourceError(f"Adzuna request failed: {exc}") from exc

        if response.status_code == 429:
            raise AdzunaSourceError("Adzuna rate limit exceeded (HTTP 429)")
        if response.status_code >= 500:
            raise AdzunaSourceError(f"Adzuna server error (HTTP {response.status_code})")
        if response.status_code != 200:
            raise AdzunaSourceError(
                f"Adzuna request rejected (HTTP {response.status_code}): "
                f"{response.text[:200]}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise AdzunaSourceError("Adzuna returned malformed JSON") from exc

        results = payload.get("results")
        if not isinstance(results, list):
            raise AdzunaSourceError("Adzuna response missing a 'results' list")
        return results

    def _to_opportunity(self, job: dict[str, Any]) -> Opportunity | None:
        job_id = job.get("id")
        title = job.get("title")
        redirect_url = job.get("redirect_url")
        company = (job.get("company") or {}).get("display_name")
        if not (job_id and title and redirect_url and company):
            return None

        return Opportunity(
            title=title,
            organization=company,
            opportunity_type=self._infer_type(title),
            description=job.get("description") or "",
            source=self.name,
            source_id=str(job_id),
            url=redirect_url,
            location=(job.get("location") or {}).get("display_name"),
            required_skills=[],
            discovered_at=self._parse_created(job.get("created")),
        )

    @staticmethod
    def _infer_type(title: str) -> OpportunityType:
        return OpportunityType.INTERNSHIP if "intern" in title.lower() else OpportunityType.JOB

    @staticmethod
    def _parse_created(created_raw: str | None) -> datetime:
        if created_raw:
            try:
                return datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(UTC)
