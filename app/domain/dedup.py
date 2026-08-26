from __future__ import annotations

from hashlib import sha256
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMS
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, urlencode(sorted(query)), "")
    )


def opportunity_fingerprint(
    *, source: str, source_id: str | None, title: str, organization: str, url: str
) -> str:
    identity = source_id.strip() if source_id else canonicalize_url(url)
    raw = "|".join(
        (
            source.strip().lower(),
            identity.lower(),
            title.strip().lower(),
            organization.strip().lower(),
        )
    )
    return sha256(raw.encode("utf-8")).hexdigest()
