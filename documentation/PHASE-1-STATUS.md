# Phase 1 — Foundation & Core Domain Status

**Branch:** `architecture`
**Status:** Complete

## Implemented

- FastAPI application foundation and health endpoint (`app/main.py`, `app/api/app.py`).
- Environment-backed application configuration (`app/config.py`).
- Pydantic domain models for profiles, opportunities, matches, and applications (`app/domain/models.py`).
- Normalized text and case-folding utilities (`app/domain/normalization.py`).
- HTTP(S) URL canonicalization with fragment removal and default-port normalization (`app/domain/normalization.py`).
- Deterministic hard-eligibility gate for remote requirements and expired deadlines (`app/domain/eligibility.py`).
- Stable, source-aware opportunity fingerprinting for deduplication (`app/domain/identity.py`).
- Deterministic matching engine (`app/domain/matching.py`).
- PostgreSQL persistence models, async session, and repository boundary (`app/db/models.py`, `app/db/session.py`, `app/db/repositories.py`).
- Alembic async migration environment and initial schema (`alembic/versions/0001_initial.py`).
- Local PostgreSQL development stack (`docker-compose.yml`).
- CI workflow running Ruff and pytest on every push/PR (`.github/workflows/ci.yml`).
- Unit test coverage: normalization, eligibility, identity, dedup, matching, API health (`tests/`).

## Exit Criteria — met

- [x] Domain behavior is covered by automated tests.
- [x] Persistence can be exercised against PostgreSQL without changing domain models.
- [x] API health checks work locally.
- [x] Ruff and pytest pass in CI.
- [x] Secrets are excluded from source control.
- [x] A clean developer can clone the repository and reproduce the test environment from documented commands.

Phase 1 is complete as of commit `924c1e0` ("fix: stabilize database migrations and code quality"). All exit criteria defined in `documentation/Development-Phases.md` are satisfied.

## Note on Phase 2 overlap

Ingestion work has already started ahead of a formal Phase 2 kickoff: the source adapter protocol, ingestion service, and a static/test source were added in commits `c4df220`, `0b078cb`, `aaee975`, `8a8d6a0`, `414a8a9`. This is Phase 2 (Opportunity Ingestion) scope per `documentation/Development-Phases.md`, not Phase 1, and is now tracked separately in `documentation/PHASE-2-STATUS.md`.
