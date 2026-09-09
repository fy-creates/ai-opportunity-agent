# Phase 2 — Opportunity Ingestion Status

**Branch:** `architecture`
**Status:** In progress

## Implemented

- `OpportunitySource` protocol defining the source adapter contract (`app/ingestion/sources.py`).
- `StaticOpportunitySource`, a deterministic in-memory source for local development and tests.
- **`AdzunaOpportunitySource`** (`app/ingestion/adapters/adzuna.py`), the first real external adapter:
  - fetches from the Adzuna Job Search API, paginating up to `adzuna_max_pages` (config in `app/config.py`),
  - stops cleanly on the first empty page,
  - maps Adzuna's job ID to `source_id` (a trusted source identifier — top of the identity preference order in `Architecture-essentials.md` §6), so most Adzuna opportunities won't need to fall back to URL/fingerprint-based identity at all,
  - infers `opportunity_type` (internship vs. job) from title text only — a soft heuristic, not a hard claim,
  - leaves `remote` and `deadline` as `None` rather than guessing, since Adzuna's API doesn't expose either,
  - treats HTTP 429/5xx/timeouts/malformed JSON/missing `results` key as hard errors (`AdzunaSourceError`), not silently-empty results, per the "fail loud rather than hide a real problem" edge-case principle,
  - implements `health_check()` (single lightweight page request) — the piece of the `SourceAdapter` contract in `Architecture.md` that was previously entirely missing,
  - `fetch_details()` from that same contract does not apply to this adapter: Adzuna's search endpoint already returns full job data in one call, so there's no separate per-listing detail fetch to make.
- `OpportunityIngestionService` (`app/ingestion/service.py`):
  - normalizes title/organization/description/source_id/location text,
  - canonicalizes the opportunity URL (tracking-parameter stripping included — see Phase 1 fix),
  - computes an identity fingerprint via `app.domain.identity.opportunity_fingerprint` (see below),
  - checks for an existing row with the same `(source, fingerprint)` and skips it as a duplicate rather than re-inserting,
  - upserts new opportunities and commits once at the end of a full run,
  - returns an `IngestionResult` count of discovered/inserted/duplicate/rejected records.
- Fingerprinting consolidated onto the single implementation in `app/domain/identity.py` (previously two divergent, independently-tested implementations existed in `identity.py` and `dedup.py`; the latter has been removed — see commit `e5edacb`).
- Unit tests: ingestion pipeline against the static source (`tests/test_ingestion.py`), and the Adzuna adapter against a mocked HTTP transport — no live network calls required (`tests/test_adzuna_source.py`).

## Gap vs. `Architecture.md` §3.4–3.5 and `documentation/Development-Phases.md` Phase 2

- **Ingestion run records and provenance.** There is still no `automation_runs`/`opportunity_sources` persistence — a run's success/failure isn't recorded anywhere durable, only returned in memory as an `IngestionResult`.
- **Retry behavior and dead-letter handling — at the run level.** Per-item normalization errors are caught and counted as `rejected`, but a page-level `AdzunaSourceError` (network failure, rate limit, auth failure) propagates out of `fetch()` uncaught. Because `OpportunityIngestionService.ingest()` only calls `session.commit()` once at the very end of a full run, a failure on page 3 currently rolls back everything ingested from pages 1–2 in that same run too. This needs run-level retry/checkpointing to fix properly, not another adapter-level patch.
- **Freshness and expiry handling.** No logic yet marks opportunities stale/expired when they stop appearing in a source.
- **Rate limiting / polite source access.** The adapter treats a 429 as a hard failure but does not yet back off and retry — it just fails the run (see retry point above).
- **A second real adapter to prove source isolation.** With only one live source implemented, "one broken source shouldn't block others" (an exit criterion below) can't yet be verified.
- **API credentials are not yet provisioned anywhere runnable.** `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` must be set via environment/`.env`; nothing in CI or local dev currently sets them, so the adapter has only been exercised against a mocked transport, never the live API.

## Next Implementation Order (revised)

1. ~~Choose and implement the first real source adapter~~ — done (Adzuna).
2. Add `automation_runs`/provenance persistence so each ingestion run is recorded, not just returned in memory.
3. Add bounded retry + dead-letter handling at the run level, distinguishing transient (429/5xx/timeout) vs. permanent (4xx auth/shape) failures — this also fixes the partial-rollback gap above by checkpointing per page rather than per full run.
4. Add freshness/expiry evaluation for opportunities that stop appearing in a source.
5. Add a second source adapter specifically to validate source isolation (one adapter failing must not block another's run).
6. Add source health checks wired into an actual scheduler/orchestration path — `health_check()` exists on the adapter now but nothing calls it yet outside tests.

## Exit Criteria

- [x] At least one real source reliably produces normalized opportunities (Adzuna, verified against a mocked transport; not yet run against the live API with real credentials).
- [x] Duplicate ingestion does not create duplicate opportunities.
- [ ] Source failures are isolated (only one source exists; can't be verified until a second adapter exists).
- [ ] Every stored opportunity has provenance beyond `source`/`source_id` (no run-level provenance yet).
- [ ] Failed jobs can be diagnosed and retried.
- [ ] Ingestion metrics are recorded.

