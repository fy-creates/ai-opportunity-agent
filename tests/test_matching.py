from datetime import UTC, datetime

from app.domain.matching import MatchingEngine
from app.domain.models import Opportunity, OpportunityType, UserProfile


def make_opportunity(**overrides) -> Opportunity:
    values = {
        "title": "Frontend React Intern",
        "organization": "Example Labs",
        "opportunity_type": OpportunityType.INTERNSHIP,
        "description": "Build web interfaces.",
        "source": "example",
        "url": "https://example.com/jobs/react-intern",
        "location": "Lagos, Nigeria",
        "remote": True,
        "required_skills": ["react", "javascript", "typescript"],
        "deadline": datetime(2026, 9, 1, tzinfo=UTC),
    }
    values.update(overrides)
    return Opportunity(**values)


def test_match_explains_skill_hits_and_gaps() -> None:
    profile = UserProfile(
        skills=["React", "JavaScript"], target_roles=["Frontend"], preferred_locations=["Lagos"]
    )
    result = MatchingEngine().evaluate(profile, make_opportunity())

    assert result.score > 50
    assert result.fit in {"moderate", "strong"}
    assert any("react" in strength.lower() for strength in result.strengths)
    assert any("typescript" in gap.lower() for gap in result.gaps)


def test_remote_requirement_excludes_non_remote_opportunity() -> None:
    profile = UserProfile(skills=["React"], remote_preference=True)
    result = MatchingEngine().evaluate(profile, make_opportunity(remote=False))

    assert result.score == 0
    assert result.fit == "weak"
    assert result.uncertainties
