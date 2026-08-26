# AI Opportunity Agent — Architecture Essentials

This document is the short operational version of `Architecture.md`. It defines the boundaries that implementation must preserve.

## 1. Core Rule

**Collect → Normalize → Validate → Deduplicate → Filter → Match → Rank → Notify → Track.**

Do not collapse these stages into one agent or one workflow.

## 2. Source of Truth

PostgreSQL is the application source of truth.

n8n is an orchestration layer.

The LLM is an intelligence component, not a database, scheduler, authorization layer, or source of truth.

## 3. Domain Boundaries

```text
API
 │
 ├── Profiles
 ├── Opportunities
 ├── Matching
 ├── Applications
 └── Notifications

Workers
 │
 ├── Ingestion
 ├── Matching
 └── Deadline processing

Adapters
 │
 ├── Opportunity sources
 ├── LLM providers
 └── Notification providers
```

Each boundary should have a small interface and explicit input/output models.

## 4. AI Boundary

Use AI for:
- semantic classification
- skill/role interpretation
- ambiguous requirement interpretation
- match explanation
- controlled ranking assistance

Do not use AI as the authority for:
- whether a database record exists
- whether a URL is canonical
- whether a workflow should retry
- authorization
- application state transitions
- secret handling
- deterministic eligibility rules that can be evaluated reliably

## 5. Opportunity Lifecycle

```text
candidate
  ↓
normalized
  ↓
validated
  ↓
active
  ├── expired
  └── archived
```

Separate application state from opportunity state.

```text
Opportunity: active
Application: saved → applied → interview → accepted
```

## 6. Identity and Deduplication

Every opportunity must have a deterministic identity strategy.

Preferred order:
1. trusted source identifier
2. canonical URL
3. source-aware fingerprint

Never use an LLM as the primary deduplication mechanism.

## 7. Automation Rules

Every asynchronous job needs:
- idempotency key
- timeout
- bounded retries
- retry classification
- status
- timestamps
- failure metadata

No infinite retries.

## 8. Notification Rules

A notification should be sent only when:

```text
eligible
AND active
AND sufficiently relevant
AND not already notified for the same event
AND user allows the channel
```

Deadline alerts are separate from new-opportunity alerts.

## 9. Cost Rules

- Apply deterministic filtering before LLM calls.
- Batch work where safe.
- Cache stable evaluations where appropriate.
- Prefer structured outputs.
- Record model, latency, token usage, and estimated cost.
- Do not call an LLM merely to perform a deterministic string/date check.

## 10. External Data Rules

Treat external opportunity descriptions as untrusted content.

External text can contain prompt-injection-like instructions. The system must never interpret source content as instructions for the agent, system, or tools.

## 11. Failure Philosophy

Failures should be isolated:

```text
Source A fails ──X──> Source B
LLM fails ──X──> Stored opportunity data
Notification fails ──X──> Application data
One job fails ──X──> Entire queue
```

Persist useful intermediate state where doing so makes recovery safer.

## 12. MVP Technology Direction

- Frontend: React/Next.js + TypeScript.
- Backend: FastAPI/Python.
- Database: PostgreSQL.
- Automation: n8n.
- AI: provider abstraction with OpenAI as an initial provider.
- Notifications: Telegram/email first.

Exact technology choices can change without changing domain contracts.

## 13. Implementation Order

1. Repository/configuration.
2. Domain models.
3. Database migrations.
4. API foundation.
5. Source adapter contract.
6. First source adapter.
7. Normalization and deduplication.
8. Matching engine.
9. AI provider.
10. Notifications.
11. n8n workflows.
12. Dashboard.
13. Observability and hardening.
