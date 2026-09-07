# Phase 2 — Opportunity Ingestion Status

**Branch:** `architecture`
**Status:** In progress

## Implemented

- `OpportunitySource` protocol defining the source adapter contract (`app/ingestion/sources.py`).
- `StaticOpportunitySource`, a deterministic in-memory source for local development and tests.
- `OpportunityIngestionService` (`app/ingestion/service.py`):
  - normalizes title/organization/description/source_id/location text,
  - canonicalizes the opportunity URL,
  - computes a source-aware fingerprint before persistence,
  - checks for an existing row with the same `(source, fingerprint)` and skips it as a duplicate rather than re-inserting,
  - upserts new opportunities and commits per ingestion run,
  - returns an `IngestionResult` count of discovered/inserted/duplicate/rejected records.
- Unit/integration tests for the ingestion pipeline against the static source (`tests/test_ingestion.py`).

## Gap vs. `Architecture.md` §3.4–3.5 and `documentation/Development-Phases.md` Phase 2

The pipeline currently implements only the normalize → canonicalize → deduplicate → upsert core. Not yet built:

- **A real external source adapter.** `StaticOpportunitySource` is test-only; no adapter fetches from an actual opportunity source yet.
- **`fetch_details()` and `health_check()`** from the `SourceAdapter` contract in `Architecture.md` — only `fetch()` (via `discover()`-equivalent) exists.
- **Ingestion run records and provenance.** There is no `automation_runs`/`opportunity_sources` persistence yet — a run's success/failure isn't recorded, only its in-memory result.
- **Retry behavior and dead-letter handling.** A per-item exception is caught and counted as `rejected`, but there is no retry classification, bounded backoff, or dead-letter state for the run itself.
- **Freshness and expiry handling.** No logic yet marks opportunities stale/expired when they stop appearing in a source.
- **Rate limiting / polite source access.** Not applicable yet since no live source exists.
- **Adversarial-input handling** (malformed HTML/JSON, timeouts, HTTP 429/5xx, broken links) — only `ValueError`/`TypeError` from normalization are handled; no network-layer failure handling exists yet since no network call exists yet.

## Next Implementation Order (per `documentation/Development-Phases.md` recommended build order)

1. Choose and implement the first real source adapter (`discover()`/`fetch_details()`/`health_check()`), isolated in `app/ingestion/`.
2. Add `automation_runs`/provenance persistence so each ingestion run is recorded, not just returned in memory.
3. Add bounded retry + dead-letter handling at the run level, distinguishing transient vs. permanent failures.
4. Add freshness/expiry evaluation for opportunities that stop appearing in a source.
5. Add adapter-level integration tests covering the adversarial cases in `Edge-cases.md` §1 (empty response, malformed payload, 429/5xx, timeout, pagination repeats).
6. Add source health checks and isolate failures so one broken adapter cannot block others.

## Exit Criteria (not yet met)

- [ ] At least one real source reliably produces normalized opportunities.
- [x] Duplicate ingestion does not create duplicate opportunities.
- [ ] Source failures are isolated (no second source exists yet to test this against).
- [ ] Every stored opportunity has provenance beyond `source`/`source_id` (no run-level provenance yet).
- [ ] Failed jobs can be diagnosed and retried.
- [ ] Ingestion metrics are recorded.
