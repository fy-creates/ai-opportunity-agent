from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserProfileRow(Base):
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    target_roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    preferred_locations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    remote_preference: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class OpportunityRow(Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        UniqueConstraint("source", "fingerprint", name="uq_opportunity_source_fingerprint"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500))
    organization: Mapped[str] = mapped_column(String(300))
    opportunity_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(200))
    source_id: Mapped[str | None] = mapped_column(String(300), nullable=True)
    url: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    remote: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    required_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active")
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)


class MatchResultRow(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    opportunity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    score: Mapped[int] = mapped_column(Integer)
    fit: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text)
    policy_version: Mapped[str] = mapped_column(String(50), default="v1")
