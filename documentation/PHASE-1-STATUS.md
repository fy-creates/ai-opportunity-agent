# Phase 1 — Foundation & Core Domain Status

**Branch:** `architecture`
**Status:** In progress

## Implemented

- FastAPI application foundation and health endpoints.
- Environment-backed application configuration.
- Pydantic domain models for profiles, opportunities, matches, and applications.
- Normalized text and case-folding utilities.
- HTTP(S) URL canonicalization with fragment removal and default-port normalization.
- Deterministic hard-eligibility gate for remote requirements and expired deadlines.
- Stable, source-aware opportunity fingerprinting for deduplication.
- Unit tests covering normalization, eligibility, and identity behavior.

## Remaining Phase 1 Work

- Persistence boundary and PostgreSQL repositories.
- Database migrations.
- Explicit application state-transition policy.
- API schemas and service boundaries around the domain.
- CI workflow running Ruff and pytest.
- Local Docker development stack for PostgreSQL.
- Full Phase 1 integration test suite.

## Exit Criteria

Phase 1 is complete only when:

- Domain behavior is covered by automated tests.
- Persistence can be exercised against PostgreSQL without changing domain models.
- API health checks work locally.
- Ruff and pytest pass in CI.
- Secrets are excluded from source control.
- A clean developer can clone the repository and reproduce the test environment from documented commands.

## Next Implementation Order

1. Persistence interfaces and database models.
2. Alembic migrations.
3. Repository integration tests using PostgreSQL.
4. Profile/opportunity API contracts.
5. CI and local Docker stack.
6. Phase 1 verification and release tag.
