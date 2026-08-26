from app.domain.normalization import canonicalize_url, normalize_key, normalize_text


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("  React   Developer\n Intern ") == "React Developer Intern"


def test_normalize_key_is_case_insensitive() -> None:
    assert normalize_key("  React Developer ") == "react developer"


def test_canonicalize_url_removes_fragment_and_default_port() -> None:
    assert canonicalize_url("HTTPS://Example.COM:443/jobs/123/#apply") == "https://example.com/jobs/123"


def test_canonicalize_url_rejects_relative_url() -> None:
    try:
        canonicalize_url("/jobs/123")
    except ValueError as exc:
        assert "absolute HTTP(S) URL" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
