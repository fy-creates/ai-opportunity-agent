from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OpportunityRow
from app.domain.dedup import opportunity_fingerprint
from app.domain.models import Opportunity
from app.domain.normalization import canonicalize_url, normalize_text
from app.ingestion.sources import OpportunitySource


@dataclass(frozen=True)
class IngestionResult:
    discovered: int = 0
    inserted: int = 0
    duplicates: int = 0
    rejected: int = 0


class OpportunityIngestionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ingest(self, source: OpportunitySource) -> IngestionResult:
        result = IngestionResult()
        async for opportunity in source.fetch():
            result = IngestionResult(
                discovered=result.discovered + 1,
                inserted=result.inserted,
                duplicates=result.duplicates,
                rejected=result.rejected,
            )
            try:
                normalized = self._normalize(opportunity)
                fingerprint = opportunity_fingerprint(
                    source=source.name,
                    source_id=normalized.source_id,
                    title=normalized.title,
                    organization=normalized.organization,
                    url=str(normalized.url),
                )
                exists = await self.session.scalar(
                    select(OpportunityRow.id).where(
                        OpportunityRow.source == source.name,
                        OpportunityRow.fingerprint == fingerprint,
                    )
                )
                if exists is not None:
                    result = IngestionResult(
                        discovered=result.discovered,
                        inserted=result.inserted,
                        duplicates=result.duplicates + 1,
                        rejected=result.rejected,
                    )
                    continue

                self.session.add(
                    OpportunityRow(
                        id=normalized.id,
                        title=normalized.title,
                        organization=normalized.organization,
                        opportunity_type=normalized.opportunity_type.value,
                        description=normalized.description,
                        source=source.name,
                        source_id=normalized.source_id,
                        url=str(normalized.url),
                        location=normalized.location,
                        remote=normalized.remote,
                        required_skills=normalized.required_skills,
                        deadline=normalized.deadline,
                        status=normalized.status.value,
                        discovered_at=normalized.discovered_at,
                        fingerprint=fingerprint,
                    )
                )
                await self.session.flush()
                result = IngestionResult(
                    discovered=result.discovered,
                    inserted=result.inserted + 1,
                    duplicates=result.duplicates,
                    rejected=result.rejected,
                )
            except (ValueError, TypeError):
                result = IngestionResult(
                    discovered=result.discovered,
                    inserted=result.inserted,
                    duplicates=result.duplicates,
                    rejected=result.rejected + 1,
                )

        await self.session.commit()
        return result

    @staticmethod
    def _normalize(opportunity: Opportunity) -> Opportunity:
        return opportunity.model_copy(
            update={
                "title": normalize_text(opportunity.title),
                "organization": normalize_text(opportunity.organization),
                "description": normalize_text(opportunity.description),
                "source_id": normalize_text(opportunity.source_id)
                if opportunity.source_id
                else None,
                "url": canonicalize_url(str(opportunity.url)),
                "location": normalize_text(opportunity.location)
                if opportunity.location
                else None,
            }
        )
