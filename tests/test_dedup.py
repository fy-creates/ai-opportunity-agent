from app.domain.dedup import canonicalize_url, opportunity_fingerprint


def test_canonicalize_url_removes_tracking_parameters() -> None:
    value = canonicalize_url("HTTPS://Example.COM/jobs/1/?utm_source=newsletter&ref=abc")
    assert value == "https://example.com/jobs/1?ref=abc"


def test_fingerprint_is_stable() -> None:
    first = opportunity_fingerprint(
        source="Example",
        source_id="123",
        title="React Intern",
        organization="Example Labs",
        url="https://example.com/1",
    )
    second = opportunity_fingerprint(
        source="Example",
        source_id="123",
        title="React Intern",
        organization="Example Labs",
        url="https://example.com/1?utm_source=x",
    )
    assert first == second
