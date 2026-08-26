from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from app.domain.models import Opportunity


class OpportunitySource(Protocol):
    name: str

    async def fetch(self) -> AsyncIterator[Opportunity]:
        """Yield opportunities discovered by this source."""
        ...


class StaticOpportunitySource:
    """Deterministic source useful for local development and tests."""

    name = "static"

    def __init__(self, opportunities: Sequence[Opportunity]) -> None:
        self._opportunities = opportunities

    async def fetch(self) -> AsyncIterator[Opportunity]:
        for opportunity in self._opportunities:
            yield opportunity
