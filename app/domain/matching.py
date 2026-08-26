from __future__ import annotations

from app.domain.models import MatchResult, Opportunity, UserProfile


class MatchingEngine:
    """Deterministic MVP matcher. AI semantic matching can be layered on later."""

    policy_version = "v1"

    def evaluate(self, profile: UserProfile, opportunity: Opportunity) -> MatchResult:
        profile_skills = {skill.lower() for skill in profile.skills}
        required = set(opportunity.required_skills)
        skill_hits = sorted(profile_skills & required)
        skill_gaps = sorted(required - profile_skills)

        target_roles = {role.lower() for role in profile.target_roles}
        role_fit = (
            any(role in opportunity.title.lower() for role in target_roles)
            if target_roles
            else False
        )

        location_fit = self._location_fit(profile, opportunity)
        remote_fit = (
            profile.remote_preference is None
            or opportunity.remote is None
            or profile.remote_preference == opportunity.remote
        )

        hard_exclusion = False
        exclusions: list[str] = []
        if profile.remote_preference is True and opportunity.remote is False:
            hard_exclusion = True
            exclusions.append("User requires remote opportunities")

        if hard_exclusion:
            return MatchResult(
                opportunity_id=opportunity.id,
                score=0,
                fit="weak",
                strengths=skill_hits,
                gaps=skill_gaps,
                uncertainties=exclusions,
                reason="Excluded by a configured hard preference.",
                policy_version=self.policy_version,
            )

        score = 25
        if required:
            score += round(40 * len(skill_hits) / len(required))
        else:
            score += 20
        if role_fit:
            score += 20
        if location_fit:
            score += 10
        elif profile.preferred_locations:
            score -= 10
        if remote_fit:
            score += 5

        score = max(0, min(100, score))
        fit = "strong" if score >= 75 else "moderate" if score >= 50 else "weak"
        strengths = [f"Matches skill: {skill}" for skill in skill_hits]
        if role_fit:
            strengths.append("Target role matches opportunity title")
        if location_fit:
            strengths.append("Location preference matches")

        return MatchResult(
            opportunity_id=opportunity.id,
            score=score,
            fit=fit,
            strengths=strengths,
            gaps=[f"Missing skill: {skill}" for skill in skill_gaps],
            reason=self._reason(score, skill_hits, skill_gaps, role_fit),
            policy_version=self.policy_version,
        )

    @staticmethod
    def _location_fit(profile: UserProfile, opportunity: Opportunity) -> bool:
        if not profile.preferred_locations or not opportunity.location:
            return False
        location = opportunity.location.lower()
        return any(preference.lower() in location for preference in profile.preferred_locations)

    @staticmethod
    def _reason(score: int, hits: list[str], gaps: list[str], role_fit: bool) -> str:
        parts = [f"Deterministic match score: {score}/100."]
        if hits:
            parts.append(f"{len(hits)} required skill(s) matched.")
        if gaps:
            parts.append(f"{len(gaps)} required skill(s) missing.")
        if role_fit:
            parts.append("Target role alignment is positive.")
        return " ".join(parts)
