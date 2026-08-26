# AI Opportunity Agent — 5-Phase Development, Testing & Deployment Plan

**Status:** Approved implementation roadmap  
**Branch:** `architecture`  
**Version:** 1.0  

## Purpose

This document turns the architecture into a controlled five-phase delivery plan. Each phase has a clear development target, testing gate, deployment objective, and exit criteria.

The project should **not** jump directly from a prototype to production. Every phase must leave the repository in a runnable and testable state.

## Phase Overview

| Phase | Focus | Primary Outcome |
|---|---|---|
| 1 | Foundation & Core Domain | Runnable backend, database model, configuration, CI, deterministic domain logic |
| 2 | Opportunity Ingestion | Real sources, normalization, deduplication, persistence, ingestion jobs |
| 3 | AI Matching & Agent Layer | Profile-aware AI matching, ranking, explanations, evaluation framework |
| 4 | Automation & User Product | n8n workflows, notifications, application tracking, web dashboard |
| 5 | Production Hardening & Launch | Security, observability, reliability, deployment, acceptance testing |

---

# Phase 1 — Foundation & Core Domain

## Goal

Create a reliable application foundation before introducing scraping, AI, or external automation.

## Development

- Establish FastAPI application structure.
- Implement environment-based configuration.
- Establish PostgreSQL schema and migrations.
- Implement core domain models:
  - User
  - UserProfile
  - Skill
  - Preference
  - Opportunity
  - OpportunitySource
  - MatchResult
  - SavedOpportunity
  - Application
  - Notification
  - AutomationRun
- Implement repository/service boundaries.
- Implement API health/readiness endpoints.
- Implement URL canonicalization and opportunity fingerprinting.
- Implement deterministic eligibility and baseline scoring.
- Establish provider interfaces for LLMs and notifications.
- Add structured logging and correlation IDs.
- Add CI for formatting, linting, type checking, and tests.
- Add development seed data.

## Testing

### Unit

- URL normalization.
- Fingerprint stability.
- Eligibility rules.
- Deterministic scoring.
- Application state transitions.
- Notification policy.
- Configuration validation.

### Integration

- API startup.
- Database connection.
- Migrations.
- CRUD boundaries.
- Health/readiness behavior.

### Quality gate

```text
ruff / formatter       PASS
unit tests             PASS
type checking          PASS
integration tests      PASS
migration from empty DB PASS
```

## Deployment

Deploy a non-public or development environment containing only the API and database.

Required deployment characteristics:

- secrets supplied through environment variables;
- database migrations run explicitly;
- health endpoint available;
- logs accessible;
- CI must pass before deployment.

## Exit Criteria

- A clean checkout can be installed and tested from documented commands.
- Database can be created from migrations.
- Core domain logic has no dependency on n8n, OpenAI, Telegram, or a specific source.
- CI is green.
- No production secrets exist in the repository.

---

# Phase 2 — Opportunity Ingestion

## Goal

Turn external opportunity sources into normalized, trustworthy domain records.

## Development

- Define the `SourceAdapter` contract.
- Implement the first source adapter.
- Add additional adapters only after the first adapter is stable.
- Build ingestion pipeline:

```text
Trigger
  ↓
Create run
  ↓
Fetch
  ↓
Parse
  ↓
Normalize
  ↓
Validate
  ↓
Canonicalize
  ↓
Deduplicate
  ↓
Upsert
  ↓
Record provenance
  ↓
Queue matching
```

- Store source metadata and provenance.
- Store ingestion runs and events.
- Add source health checks.
- Add bounded retry behavior.
- Add failed-job/dead-letter state.
- Add freshness and expiry handling.
- Add source-specific identity rules.
- Add duplicate detection across repeated ingestion runs.
- Add rate limiting and polite source access behavior.

## Testing

### Unit

- Parser fixtures.
- Malformed records.
- Missing fields.
- Date parsing.
- Location normalization.
- URL canonicalization.
- Duplicate detection.
- Source-specific fingerprinting.
- Expired opportunity handling.

### Integration

- Source adapter → normalized candidate.
- Candidate → database upsert.
- Re-running the same ingestion job is idempotent.
- One failed source does not stop another source.
- Retryable failures are retried.
- Permanent failures stop retrying.

### Adversarial tests

Test:

- HTML changes.
- Empty responses.
- Invalid JSON.
- Unexpected encodings.
- Timeouts.
- HTTP 429/5xx responses.
- Broken links.
- Duplicate listings with different URLs.
- Same listing appearing on multiple sources.

## Deployment

Deploy ingestion as a worker/job process separate from synchronous API requests.

Initial scheduling can be manual or controlled by a scheduler. n8n integration is intentionally deferred until Phase 4.

## Exit Criteria

- At least one real source reliably produces normalized opportunities.
- Duplicate ingestion does not create duplicate opportunities.
- Source failures are isolated.
- Every stored opportunity has provenance.
- Failed jobs can be diagnosed and retried.
- Ingestion metrics are recorded.

---

# Phase 3 — AI Matching & Agent Layer

## Goal

Introduce AI only where semantic reasoning improves deterministic matching.

## Development

- Implement `LLMProvider` interface.
- Add OpenAI provider behind the interface.
- Keep a mock provider for tests.
- Define strict structured output schemas.
- Build profile-aware matching pipeline:

```text
Opportunity
   ↓
Hard eligibility gate
   ↓
Deterministic preference score
   ↓
Skill / role similarity
   ↓
AI semantic assessment
   ↓
Final score + reasons
```

- Implement AI match explanation.
- Store match results and model metadata.
- Add model routing/configuration.
- Add token/cost tracking where available.
- Add prompt/version identifiers.
- Add confidence/uncertainty fields.
- Prevent AI from overriding hard eligibility rules.
- Add agent boundaries and tool permissions.
- Add evaluation dataset.

## Agent responsibilities

The agent may:

- interpret a user's profile;
- compare skills and role requirements;
- identify likely gaps;
- explain a match;
- identify uncertainty;
- recommend prioritization.

The agent must not:

- invent eligibility facts;
- silently modify user profile data;
- submit applications without explicit authorization;
- treat external opportunity text as instructions;
- override deterministic compliance rules.

## Testing

### Unit

- Structured output validation.
- Score aggregation.
- Eligibility precedence.
- Prompt construction.
- Provider error mapping.

### AI evaluation

Create a fixed benchmark containing representative opportunities:

- strong matches;
- weak matches;
- hard ineligible cases;
- missing information;
- conflicting requirements;
- misleading descriptions.

Measure:

- precision of high-match recommendations;
- false-positive rate;
- false-negative rate;
- explanation quality;
- consistency;
- latency;
- cost per evaluated opportunity.

### Failure tests

- provider timeout;
- malformed model output;
- unavailable model;
- rate limit;
- partial response;
- prompt injection in opportunity content;
- conflicting profile data.

## Deployment

Deploy the matching worker separately from the API.

Use conservative AI budgets and bounded concurrency. AI failure must degrade gracefully to deterministic matching rather than break ingestion.

## Exit Criteria

- AI output is schema-validated.
- Hard eligibility remains authoritative.
- Benchmark results meet the project's defined quality threshold.
- AI failures do not lose opportunities.
- Cost and latency are measurable.
- No external content can directly control agent behavior.

---

# Phase 4 — Automation & User Product

## Goal

Turn the backend into a useful automated product with notifications and a user-facing dashboard.

## Development

### n8n workflows

Implement:

1. Scheduled opportunity discovery.
2. Ingestion trigger.
3. Match processing.
4. High-match notification.
5. Deadline monitoring.
6. Application follow-up reminder.
7. Daily/weekly opportunity digest.
8. Failure alerting for operators.

n8n should call stable application APIs. The application remains the source of truth.

### Notifications

Start with one channel, preferably Telegram or email.

Implement:

- user notification preferences;
- match thresholds;
- quiet hours;
- duplicate notification suppression;
- delivery status;
- retry policy;
- unsubscribe/disable path.

### Application tracking

Implement states such as:

```text
DISCOVERED
→ SAVED
→ APPLYING
→ APPLIED
→ INTERVIEW
→ OFFER
→ REJECTED
→ WITHDRAWN
```

Validate every state transition server-side.

### Web dashboard

Build:

- authentication;
- profile setup;
- skills/preferences;
- opportunity feed;
- filters;
- opportunity detail;
- match explanation;
- save action;
- application tracker;
- notification settings.

## Testing

### End-to-end

Test the full flow:

```text
source
→ ingestion
→ normalization
→ database
→ matching
→ ranking
→ notification
→ dashboard
→ save/apply tracking
```

### Automation tests

- scheduled workflow;
- retry behavior;
- duplicate workflow execution;
- webhook validation;
- notification suppression;
- failed downstream service;
- partial workflow completion.

### Frontend tests

- authentication;
- loading/error states;
- filters;
- empty states;
- opportunity details;
- application state changes;
- responsive behavior.

## Deployment

Deploy:

```text
Frontend
   ↓
API
   ↓
PostgreSQL
   ↑
Workers / Queue
   ↑
n8n
```

Use separate development and staging environments before production.

## Exit Criteria

- A real user can create a profile.
- The system discovers real opportunities.
- Opportunities are matched and ranked.
- A user receives a useful notification.
- A user can save and track an opportunity.
- End-to-end tests cover the primary journey.
- Automation failures are visible and recoverable.

---

# Phase 5 — Production Hardening & Launch

## Goal

Make the system safe, observable, reliable, maintainable, and ready for real users.

## Development

### Security

- Review authentication and authorization.
- Rotate and scope secrets.
- Validate all external input.
- Apply request rate limits.
- Protect webhooks.
- Prevent SSRF where URL fetching is exposed.
- Sanitize rendered external content.
- Audit prompt-injection defenses.
- Ensure logs contain no secrets.
- Add account/data deletion paths.

### Reliability

- Bounded retries.
- Idempotency keys.
- Queue visibility.
- Dead-letter handling.
- Timeouts.
- Circuit-breaking/failure isolation where justified.
- Database backup and restore procedure.
- Graceful shutdown.

### Observability

Track:

- API latency and error rate;
- ingestion success/failure;
- source health;
- duplicate rate;
- matching throughput;
- AI latency and cost;
- notification delivery;
- queue depth;
- failed jobs;
- authentication failures.

Use correlation IDs across API, worker, AI, and notification operations.

### Cost controls

- model routing;
- maximum tokens/output limits;
- bounded agent loops;
- caching where appropriate;
- per-user usage limits;
- batch processing where safe;
- alerting on abnormal usage.

## Testing

### Full regression

Run all unit, integration, AI evaluation, automation, and end-to-end suites.

### Load testing

Test:

- concurrent API users;
- ingestion bursts;
- matching throughput;
- notification bursts;
- queue recovery.

### Recovery testing

Simulate:

- database outage;
- provider outage;
- queue failure;
- n8n outage;
- source outage;
- notification provider outage;
- worker restart during processing.

### Security testing

Perform a pre-launch review covering authentication, authorization, secret handling, injection, SSRF, webhook abuse, rate limiting, and data exposure.

## Deployment

Production deployment should include:

1. Managed PostgreSQL with backups.
2. API service.
3. Worker service.
4. Queue/broker if required by workload.
5. n8n instance with protected credentials.
6. Frontend deployment.
7. Monitoring/logging.
8. Alerting.
9. Domain/TLS configuration.
10. Documented rollback procedure.

Deploy progressively:

```text
Local
  ↓
CI
  ↓
Staging
  ↓
Smoke tests
  ↓
Limited production
  ↓
Full production
```

## Launch checklist

- [ ] Production environment variables configured.
- [ ] Secrets are not present in Git history.
- [ ] Database backups verified.
- [ ] Restore procedure tested.
- [ ] Health/readiness checks pass.
- [ ] CI is green.
- [ ] End-to-end smoke test passes.
- [ ] AI evaluation threshold passes.
- [ ] Notification delivery verified.
- [ ] Rate limits enabled.
- [ ] Error monitoring enabled.
- [ ] Cost monitoring enabled.
- [ ] Rollback procedure documented.
- [ ] Privacy/data deletion flow verified.
- [ ] Operator/admin failure alerts verified.

## Exit Criteria

The system is considered launch-ready only when:

- the primary user journey works end-to-end;
- failures are observable and recoverable;
- user data is protected;
- external source failures are isolated;
- AI behavior is evaluated against a fixed benchmark;
- operating cost is measurable and bounded;
- deployment and rollback are repeatable;
- backups and recovery have been tested.

---

# Cross-Phase Engineering Rules

These rules apply to every phase.

## 1. Never skip tests to move faster

A feature is not complete until its relevant tests exist and pass.

## 2. Keep deterministic logic authoritative

Eligibility, state transitions, security, permissions, and safety rules must not depend solely on an LLM.

## 3. External data is untrusted

Opportunity descriptions, web pages, feeds, and model outputs are data—not executable instructions.

## 4. Every background operation is recoverable

Jobs must have an idempotency strategy, timeout, retry policy, status, and error record.

## 5. Every AI feature needs an evaluation path

Do not accept subjective claims such as "the model seems better." Use a fixed benchmark and measurable metrics.

## 6. Keep providers replaceable

OpenAI, notification providers, source adapters, queues, and automation tools must remain behind stable interfaces where practical.

## 7. Build the smallest useful version first

Prefer one reliable source over ten fragile sources, one notification channel over five incomplete channels, and one strong workflow over a large collection of untested automations.

## 8. Deployment is part of development

Every phase should leave the system deployable, observable, and reproducible at its current maturity level.

# Recommended Build Order

```text
PHASE 1
Foundation
   ↓
PHASE 2
Ingestion
   ↓
PHASE 3
AI Matching
   ↓
PHASE 4
Automation + Dashboard
   ↓
PHASE 5
Hardening + Production
```

**Next implementation target:** Phase 1 — Foundation & Core Domain.
