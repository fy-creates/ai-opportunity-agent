from __future__ import annotations

import hashlib

from app.domain.models import Opportunity
from app.domain.normalization import canonicalize_url, normalize_key


def opportunity_fingerprint(opportunity: Opportunity) -> str:
    """Create a stable identity for deduplication when a source ID is unavailable."""
    canonical_url = canonicalize_url(str(opportunity.url))
    source_id = normalize_key(opportunity.source_id or "")
    if source_id:
        material = f"source:{normalize_key(opportunity.source)}|id:{source_id}"
    else:
        material = "|".join(
            [
                normalize_key(opportunity.source),
                normalize_key(opportunity.organization),
                normalize_key(opportunity.title),
                normalize_key(opportunity.location or ""),
                opportunity.deadline.isoformat() if opportunity.deadline else "",
                canonical_url,
            ]
        )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
