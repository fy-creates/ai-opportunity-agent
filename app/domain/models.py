from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


class OpportunityType(StrEnum):
    JOB = "job"
    INTERNSHIP = "internship"
    SCHOLARSHIP = "scholarship"
    FELLOWSHIP = "fellowship"
    GRANT = "grant"
    COMPETITION = "competition"
    BOOTCAMP = "bootcamp"
    OTHER = "other"


class OpportunityStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class ApplicationStatus(StrEnum):
    SAVED = "saved"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class UserProfile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    skills: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: bool | None = None
    experience_level: str | None = None
    industries: list[str] = Field(default_factory=list)

    @field_validator("skills", "target_roles", "preferred_locations", "industries")
    @classmethod
    def normalize_items(cls, values: list[str]) -> list[str]:
        return sorted({value.strip() for value in values if value.strip()})


class Opportunity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=500)
    organization: str = Field(min_length=1, max_length=300)
    opportunity_type: OpportunityType = OpportunityType.OTHER
    description: str = ""
    source: str = Field(min_length=1, max_length=200)
    source_id: str | None = Field(default=None, max_length=300)
    url: HttpUrl
    location: str | None = Field(default=None, max_length=300)
    remote: bool | None = None
    required_skills: list[str] = Field(default_factory=list)
    deadline: datetime | None = None
    status: OpportunityStatus = OpportunityStatus.ACTIVE
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("deadline", "discovered_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if value.tzinfo is None:
            raise ValueError("datetime must include timezone information")
        return value

    @field_validator("required_skills")
    @classmethod
    def normalize_skills(cls, values: list[str]) -> list[str]:
        return sorted({value.strip().lower() for value in values if value.strip()})


class MatchResult(BaseModel):
    opportunity_id: UUID
    score: int = Field(ge=0, le=100)
    fit: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    reason: str
    policy_version: str = "v1"


class Application(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    opportunity_id: UUID
    status: ApplicationStatus = ApplicationStatus.SAVED
    follow_up_at: datetime | None = None
    notes: str = ""

    @field_validator("follow_up_at")
    @classmethod
    def follow_up_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("follow_up_at must include timezone information")
        return value
