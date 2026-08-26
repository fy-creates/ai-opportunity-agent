from datetime import UTC, datetime

import pytest

from app.domain.models import Opportunity, OpportunityType
from app.ingestion.service import OpportunityIngestionService
from app.ingestion.sources import StaticOpportunitySource


class FakeSession:
    def __init__(self, existing_ids=None):
        self.existing_ids = existing_ids or set()
        self.rows = []
        self.committed = False

    async def scalar(self, statement):
        fingerprint = statement.whereclause.right.value
        for row in self.rows:
            if row.fingerprint == fingerprint:
                return row.id
        return next(iter(self.existing_ids), None)

    def add(self, row):
        self.rows.append(row)

    async def flush(self):
        return None

    async def commit(self):
        self.committed = True


def make_opportunity(**overrides):
    values = {
        "title": "  Frontend   Engineer  ",
        "organization": "  Example   Labs ",
        "opportunity_type": OpportunityType.JOB,
        "description": " Build   great software. ",
        "source": "ignored-by-source",
        "source_id": " job-123 ",
        "url": "https://Example.com/jobs/123/?utm_source=test#apply",
        "location": " Lagos  ",
        "remote": True,
        "required_skills": ["React", " react ", "TypeScript"],
        "deadline": datetime(2026, 9, 1, tzinfo=UTC),
    }
    values.update(overrides)
    return Opportunity(**values)


@pytest.mark.asyncio
async def test_ingestion_normalizes_and_persists():
    session = FakeSession()
    service = OpportunityIngestionService(session)

    result = await service.ingest(StaticOpportunitySource([make_opportunity()]))

    assert result.discovered == 1
    assert result.inserted == 1
    assert result.duplicates == 0
    assert result.rejected == 0
    assert session.committed
    row = session.rows[0]
    assert row.title == "Frontend Engineer"
    assert row.organization == "Example Labs"
    assert row.description == "Build great software."
    assert row.url == "https://example.com/jobs/123"
    assert row.required_skills == ["react", "typescript"]
    assert row.source == "static"
    assert len(row.fingerprint) == 64


@pytest.mark.asyncio
async def test_ingestion_deduplicates_same_opportunity():
    session = FakeSession()
    service = OpportunityIngestionService(session)
    source = StaticOpportunitySource([make_opportunity(), make_opportunity()])

    result = await service.ingest(source)

    assert result.discovered == 2
    assert result.inserted == 1
    assert result.duplicates == 1
    assert result.rejected == 0
