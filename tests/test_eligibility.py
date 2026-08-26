from datetime import datetime, timedelta, timezone

from app.domain.eligibility import evaluate_hard_eligibility
from app.domain.models import Opportunity, OpportunityType, UserProfile


def make_opportunity(**overrides: object) -> Opportunity:
    values = {
        "title": "Frontend Intern",
        "organization": "Example",
        "opportunity_type": OpportunityType.INTERNSHIP,
        "source": "test",
        "url": "https://example.com/jobs/1",
        "remote": True,
    }
    values.update(overrides)
    return Opportunity(**values)


def test_remote_requirement_excludes_non_remote() -> None:
    ok, reasons = evaluate_hard_eligibility(UserProfile(remote_preference=True), make_opportunity(remote=False))
    assert not ok
    assert "User requires remote opportunities" in reasons


def test_expired_deadline_excludes_opportunity() -> None:
    deadline = datetime.now(timezone.utc) - timedelta(minutes=1)
    ok, reasons = evaluate_hard_eligibility(UserProfile(), make_opportunity(deadline=deadline))
    assert not ok
    assert "Opportunity deadline has passed" in reasons


def test_valid_opportunity_passes() -> None:
    deadline = datetime.now(timezone.utc) + timedelta(days=3)
    ok, reasons = evaluate_hard_eligibility(UserProfile(), make_opportunity(deadline=deadline))
    assert ok
    assert reasons == []
