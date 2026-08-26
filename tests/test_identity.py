from app.domain.identity import opportunity_fingerprint
from app.domain.models import Opportunity


def make_opportunity(**overrides: object) -> Opportunity:
    values = {
        "title": "Frontend Intern",
        "organization": "Example",
        "source": "test",
        "url": "https://example.com/jobs/1",
    }
    values.update(overrides)
    return Opportunity(**values)


def test_same_source_id_has_same_fingerprint() -> None:
    first = make_opportunity(source_id="JOB-123")
    second = make_opportunity(source_id="job-123")
    assert opportunity_fingerprint(first) == opportunity_fingerprint(second)


def test_different_source_ids_do_not_collide() -> None:
    first = make_opportunity(source_id="JOB-123")
    second = make_opportunity(source_id="JOB-124")
    assert opportunity_fingerprint(first) != opportunity_fingerprint(second)
