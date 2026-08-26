from __future__ import annotations

from datetime import datetime, timezone

from app.domain.models import Opportunity, UserProfile


def evaluate_hard_eligibility(profile: UserProfile, opportunity: Opportunity) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if profile.remote_preference is True and opportunity.remote is False:
        reasons.append("User requires remote opportunities")

    if opportunity.deadline is not None:
        deadline = opportunity.deadline
        if deadline.tzinfo is not None and deadline <= datetime.now(timezone.utc):
            reasons.append("Opportunity deadline has passed")

    return not reasons, reasons
