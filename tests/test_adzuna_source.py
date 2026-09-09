import httpx
import pytest

from app.config import Settings
from app.ingestion.adapters.adzuna import AdzunaOpportunitySource, AdzunaSourceError


def make_settings(**overrides) -> Settings:
    values = {
        "adzuna_app_id": "test-id",
        "adzuna_app_key": "test-key",
        "adzuna_country": "us",
        "adzuna_results_per_page": 2,
        "adzuna_max_pages": 3,
    }
    values.update(overrides)
    return Settings(**values)


def job(job_id="1", title="Frontend Intern", company="Acme", url="https://example.com/1"):
    return {
        "id": job_id,
        "title": title,
        "redirect_url": url,
        "company": {"display_name": company},
        "location": {"display_name": "Lagos, Nigeria"},
        "description": "Build things.",
        "created": "2026-08-01T12:00:00Z",
    }


def make_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_missing_credentials_raises() -> None:
    with pytest.raises(AdzunaSourceError):
        AdzunaOpportunitySource(Settings(adzuna_app_id=None, adzuna_app_key=None))


@pytest.mark.asyncio
async def test_fetch_yields_mapped_opportunities_and_skips_incomplete_entries() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.path.rsplit("/", 1)[-1]
        if page == "1":
            return httpx.Response(
                200,
                json={
                    "results": [
                        job(job_id="1", title="Frontend Intern"),
                        {"id": "2", "title": "Missing company field"},  # incomplete, skipped
                    ]
                },
            )
        return httpx.Response(200, json={"results": []})

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    opportunities = [op async for op in source.fetch()]

    assert len(opportunities) == 1
    op = opportunities[0]
    assert op.title == "Frontend Intern"
    assert op.organization == "Acme"
    assert op.source == "adzuna"
    assert op.source_id == "1"
    assert op.opportunity_type.value == "internship"
    assert op.remote is None
    assert op.deadline is None


@pytest.mark.asyncio
async def test_fetch_paginates_until_empty_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.path.rsplit("/", 1)[-1])
        if page <= 2:
            return httpx.Response(200, json={"results": [job(job_id=str(page))]})
        return httpx.Response(200, json={"results": []})

    source = AdzunaOpportunitySource(
        make_settings(adzuna_max_pages=5), client=make_client(handler)
    )
    opportunities = [op async for op in source.fetch()]

    assert [op.source_id for op in opportunities] == ["1", "2"]


@pytest.mark.asyncio
async def test_fetch_stops_at_max_pages_even_if_results_continue() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.path.rsplit("/", 1)[-1])
        return httpx.Response(200, json={"results": [job(job_id=str(page))]})

    source = AdzunaOpportunitySource(
        make_settings(adzuna_max_pages=2), client=make_client(handler)
    )
    opportunities = [op async for op in source.fetch()]

    assert len(opportunities) == 2


@pytest.mark.asyncio
async def test_rate_limit_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="slow down")

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    with pytest.raises(AdzunaSourceError, match="rate limit"):
        async for _ in source.fetch():
            pass


@pytest.mark.asyncio
async def test_server_error_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    with pytest.raises(AdzunaSourceError, match="server error"):
        async for _ in source.fetch():
            pass


@pytest.mark.asyncio
async def test_malformed_json_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    with pytest.raises(AdzunaSourceError, match="malformed JSON"):
        async for _ in source.fetch():
            pass


@pytest.mark.asyncio
async def test_missing_results_key_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    with pytest.raises(AdzunaSourceError, match="results"):
        async for _ in source.fetch():
            pass


@pytest.mark.asyncio
async def test_health_check_true_on_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": [job()]})

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    assert await source.health_check() is True


@pytest.mark.asyncio
async def test_health_check_false_on_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="down")

    source = AdzunaOpportunitySource(make_settings(), client=make_client(handler))
    assert await source.health_check() is False


@pytest.mark.asyncio
async def test_unparseable_created_falls_back_to_now() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        entry = job()
        entry["created"] = "not-a-date"
        return httpx.Response(200, json={"results": [entry]})

    source = AdzunaOpportunitySource(
        make_settings(adzuna_max_pages=1), client=make_client(handler)
    )
    opportunities = [op async for op in source.fetch()]
    assert len(opportunities) == 1
    assert opportunities[0].discovered_at is not None
