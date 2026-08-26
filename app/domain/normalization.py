from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit, urlunsplit


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_key(value: str) -> str:
    return normalize_text(value).casefold()


def canonicalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("url must be an absolute HTTP(S) URL")
    host = parts.hostname.lower() if parts.hostname else ""
    port = parts.port
    if port and not ((parts.scheme == "http" and port == 80) or (parts.scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = parts.path or "/"
    path = re.sub(r"/{2,}", "/", path)
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), host, path, parts.query, ""))
