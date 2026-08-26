from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OpportunityRow, UserProfileRow
from app.domain.identity import opportunity_fingerprint
from app.domain.models import Opportunity, UserProfile


class UserProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID) -> UserProfile | None:
        row = await self.session.get(UserProfileRow, user_id)
        if row is None:
            return None
        return UserProfile.model_validate(row, from_attributes=True)

    async def save(self, profile: UserProfile) -> UserProfile:
        row = UserProfileRow(
            id=profile.id,
            skills=profile.skills,
            target_roles=profile.target_roles,
            preferred_locations=profile.preferred_locations,
            remote_preference=profile.remote_preference,
            experience_level=profile.experience_level,
            industries=profile.industries,
        )
        await self.session.merge(row)
        await self.session.commit()
        return profile


class OpportunityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, opportunity_id: UUID) -> Opportunity | None:
        row = await self.session.get(OpportunityRow, opportunity_id)
        if row is None:
            return None
        return self._to_domain(row)

    async def upsert(self, opportunity: Opportunity) -> Opportunity:
        fingerprint = opportunity_fingerprint(opportunity)
        result = await self.session.execute(
            select(OpportunityRow).where(
                OpportunityRow.source == opportunity.source,
                OpportunityRow.fingerprint == fingerprint,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = OpportunityRow(
                id=opportunity.id,
                title=opportunity.title,
                organization=opportunity.organization,
                opportunity_type=opportunity.opportunity_type.value,
                description=opportunity.description,
                source=opportunity.source,
                source_id=opportunity.source_id,
                url=str(opportunity.url),
                location=opportunity.location,
                remote=opportunity.remote,
                required_skills=opportunity.required_skills,
                deadline=opportunity.deadline,
                status=opportunity.status.value,
                discovered_at=opportunity.discovered_at,
                fingerprint=fingerprint,
            )
            self.session.add(row)
        else:
            row.title = opportunity.title
            row.description = opportunity.description
            row.deadline = opportunity.deadline
            row.status = opportunity.status.value
        await self.session.commit()
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: OpportunityRow) -> Opportunity:
        return Opportunity(
            id=row.id,
            title=row.title,
            organization=row.organization,
            opportunity_type=row.opportunity_type,
            description=row.description,
            source=row.source,
            source_id=row.source_id,
            url=row.url,
            location=row.location,
            remote=row.remote,
            required_skills=row.required_skills,
            deadline=row.deadline,
            status=row.status,
            discovered_at=row.discovered_at,
        )
