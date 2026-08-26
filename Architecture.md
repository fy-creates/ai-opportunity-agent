# AI Opportunity Agent — Architecture

**Status:** Draft
**Branch:** `architecture`
**Version:** 0.1

## 1. Architectural Principles

1. Separate collection, domain logic, AI reasoning, automation, and delivery.
2. Prefer deterministic rules for facts, eligibility, state transitions, and safety boundaries.
3. Use AI for semantic tasks where probabilistic reasoning provides measurable value.
4. Treat every external source as unreliable input.
5. Make workflows idempotent and retryable.
6. Preserve provenance for every opportunity.
7. Keep provider integrations behind interfaces.
8. Human approval is required for irreversible external actions.
9. Keep the core domain independent from n8n, OpenAI, Telegram, or any single source.
10. Design for low operating cost from day one.

## 2. Proposed System

```text
                         ┌──────────────────┐
                         │   Web Dashboard  │
                         │ React / Next.js  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    API Layer     │
                         │     FastAPI      │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
       Profile Service       Opportunity API     Tracking API
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │   PostgreSQL     │
                         └────────┬─────────┘
                                  ▲
                                  │
                         ┌────────┴────────┐
                         │  Worker / Queue │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
       Source Adapters       Matching Engine       Notifications
             │                    │                    │
             ▼                    ▼                    ▼
       External Sources       LLM Provider       Telegram / Email
                                  │
                                  ▼
                           AI Evaluation
```

## 3. Component Responsibilities

### 3.1 Frontend

Responsible for:
- authentication UI
- profile management
- opportunity browsing
- filters
- opportunity details
- match explanations
- saved opportunities
- application tracking
- notification preferences

The frontend never receives provider secrets.

### 3.2 API Layer

FastAPI owns:
- request validation
- authentication/authorization
- profile CRUD
- opportunity queries
- application state transitions
- notification preferences
- administrative/health endpoints

It should not contain source-specific scraping logic.

### 3.3 Domain Layer

Core entities:
- User
- UserProfile
- Skill
- Preference
- Opportunity
- OpportunitySource
- MatchResult
- Application
- Notification
- AutomationRun

Domain services include:
- eligibility evaluation
- match scoring
- opportunity deduplication
- freshness evaluation
- application state transitions
- notification policy

### 3.4 Source Adapter Layer

Each source implements a common contract:

```text
SourceAdapter
├── discover()
├── fetch_details()
├── normalize()
└── health_check()
```

Adapters output normalized domain candidates. They must not directly mutate unrelated domain state.

### 3.5 Ingestion Pipeline

```text
Trigger
  ↓
Create run record
  ↓
Fetch source
  ↓
Parse
  ↓
Normalize
  ↓
Validate
  ↓
Canonicalize URL
  ↓
Deduplicate
  ↓
Upsert opportunity
  ↓
Record provenance
  ↓
Queue matching
```

A failed source should not fail the entire ingestion run.

### 3.6 Matching Engine

Use a staged approach:

```text
Opportunity
   ↓
Hard eligibility gate
   ↓
Deterministic preference score
   ↓
Skill/role similarity
   ↓
AI semantic assessment (only when useful)
   ↓
Final score + reasons
```

The AI result is advisory. Hard constraints remain authoritative.

### 3.7 LLM Provider

Use a provider interface:

```text
LLMProvider
├── generate_structured()
├── classify()
├── evaluate_match()
└── health_check()
```

Providers should be replaceable without changing domain code.

### 3.8 Automation Layer

n8n can orchestrate:
- scheduled discovery
- workflow triggers
- notifications
- deadline checks
- external integrations
- human approval steps

The core application remains the source of truth. n8n should call stable APIs rather than write directly to core tables unless an explicitly designed integration requires it.

### 3.9 Notification Service

Notification policy should consider:
- match threshold
- opportunity freshness
- deadline urgency
- user preferences
- previous notifications
- quiet hours
- channel availability

## 4. Data Model

```text
users
  └── user_profiles
        ├── profile_skills
        ├── profile_preferences
        └── profile_education

opportunities
  ├── opportunity_sources
  ├── opportunity_skills
  └── opportunity_snapshots

users ──< match_results >── opportunities
users ──< saved_opportunities >── opportunities
users ──< applications >── opportunities
users ──< notifications >── opportunities
automation_runs ──< automation_events
```

### Opportunity identity

Prefer a stable canonical URL when available. When URLs are unstable, use a deterministic identity fingerprint derived from normalized organization, title, location, deadline, and source-specific identifiers. Identity strategy must be source-aware and versioned.

## 5. Matching Model

The first implementation should avoid pretending that one LLM-generated number is objectively correct.

Suggested conceptual score:

```text
match_score = weighted(
    eligibility,
    role_fit,
    skill_fit,
    experience_fit,
    location_fit,
    preference_fit,
    freshness
)
```

Hard ineligibility should produce an explicit exclusion reason rather than a low arbitrary score.

AI output should be structured:

```json
{
  "fit": "strong|moderate|weak",
  "score": 0,
  "strengths": [],
  "gaps": [],
  "uncertainties": [],
  "reason": ""
}
```

The exact schema is an implementation contract and should be validated server-side.

## 6. Automation Architecture

```text
Scheduler
   ↓
Discovery workflow
   ↓
API / ingestion endpoint
   ↓
Queue
   ↓
Workers
   ├── normalize
   ├── deduplicate
   ├── match
   └── notify
```

Long-running work should not block API requests.

Each job should have:
- idempotency key
- attempt count
- timeout
- retry policy
- status
- started/finished timestamps
- error metadata

## 7. Reliability

### Retries

Retry transient failures with bounded exponential backoff. Do not retry permanent validation errors indefinitely.

### Idempotency

A workflow may be executed multiple times. The resulting domain state must remain correct.

### Dead-letter handling

Jobs that exhaust retries should enter a recoverable failed state and be visible to operators.

### Source isolation

One broken source adapter must not block other sources.

## 8. Security

- Provider keys remain server-side.
- Secrets are environment-managed.
- Authentication is required for private user data.
- Authorization checks are performed server-side.
- Input is validated at API boundaries.
- External content is treated as untrusted data.
- AI-generated text is never treated as executable instructions.
- Logs must not contain secrets or unnecessary personal data.

## 9. Privacy

Collect only data required for matching and tracking. Provide deletion paths. Avoid storing application credentials or sensitive documents in MVP.

## 10. Observability

Record:
- ingestion runs
- source failures
- opportunity counts
- duplicate counts
- match evaluations
- AI latency
- AI token/cost metadata where available
- notification delivery status
- workflow failures

Use correlation IDs across API → worker → AI → notification operations.

## 11. Testing Strategy

### Unit
- normalization
- URL canonicalization
- deduplication
- eligibility
- scoring
- state transitions
- notification policy

### Integration
- source adapter → ingestion
- database persistence
- API authentication
- queue/worker behavior
- notification adapters

### AI evaluation
Maintain a fixed evaluation dataset with expected judgments. Track precision, false positives, false negatives, explanation quality, and cost.

### Failure tests
Test timeouts, malformed source data, provider errors, duplicate jobs, partial workflow completion, and stale opportunities.

## 12. Deployment Shape

Initial production shape:

```text
Frontend → API → PostgreSQL
              ↑
          Worker/Queue
              ↑
             n8n
```

The system should be deployable without n8n for core synchronous functionality, allowing automation orchestration to evolve independently.
