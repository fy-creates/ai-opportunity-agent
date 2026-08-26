# AI Opportunity Agent — Edge Cases and Failure Matrix

This document closes the reliability gaps that commonly appear in opportunity discovery systems.

## 1. Source and Ingestion

| Case | Required behavior |
|---|---|
| Source unavailable | Mark source run failed, retry if transient, continue other sources. |
| Source returns 429 | Respect retry-after when available; use bounded backoff. |
| Source returns malformed HTML/JSON | Reject the candidate safely and record parser error. |
| Source schema changes | Adapter fails visibly; do not silently map incorrect fields. |
| Empty source response | Record successful empty run; do not treat as deletion. |
| Same listing appears in multiple sources | Deduplicate while retaining all provenance. |
| Listing disappears from source | Do not immediately delete; mark freshness according to policy. |
| Source publishes future-dated listing | Store it as inactive/upcoming when appropriate. |
| Source publishes expired listing | Persist if useful for history, but do not recommend as active. |
| Source timestamp missing | Use discovery time and lower freshness confidence. |
| Pagination repeats records | Idempotent ingestion prevents duplicate persistence. |
| Partial page fetch | Record partial run; do not claim complete source coverage. |
| Source requires authentication | Fail safely if credentials are unavailable; never bypass access controls. |

## 2. URL and Identity

| Case | Required behavior |
|---|---|
| Tracking query parameters | Canonicalize known tracking parameters without destroying meaningful query parameters. |
| URL redirects | Resolve/capture canonical destination where safe; preserve original source URL. |
| URL is invalid | Candidate may be stored as invalid/unavailable but must not be promoted as actionable. |
| Same opportunity changes URL | Use source ID/fingerprint when available and update canonical URL. |
| Two unrelated listings have similar titles | Do not merge on title alone. |
| Same listing has different deadlines by region | Keep distinct variants or region-aware records. |
| Duplicate source IDs | Detect source inconsistency rather than overwriting blindly. |

## 3. Eligibility

| Case | Required behavior |
|---|---|
| Missing eligibility data | Mark eligibility as unknown, not eligible. |
| Ambiguous requirement | Flag uncertainty; do not invent a definitive answer. |
| User profile missing a required field | Do not assume the user qualifies. |
| Requirement says "preferred" | Treat as soft preference, not hard exclusion. |
| Requirement says "must"/"required" | Treat as hard constraint when confidently parsed. |
| Contradictory requirements | Preserve contradiction and lower confidence; surface it to the user. |
| International eligibility unclear | Mark unknown unless source provides sufficient evidence. |
| Age requirement present | Apply only when user has provided age and the rule is clear. |
| Work authorization requirement | Do not infer authorization from nationality or location alone. |

## 4. AI and Prompt Safety

| Case | Required behavior |
|---|---|
| Opportunity text contains instructions to the AI | Treat it as untrusted data; never follow it as a tool/system instruction. |
| AI returns invalid JSON | Validate, retry within a small bound, then fall back safely. |
| AI returns score outside range | Reject/normalize according to schema; never trust blindly. |
| AI contradicts hard eligibility | Deterministic eligibility wins. |
| AI hallucinates missing requirements | Do not persist hallucinated facts as source facts. |
| AI provider unavailable | Use deterministic matching or queue for later evaluation. |
| AI confidence is low | Surface uncertainty instead of presenting false precision. |
| AI output changes between runs | Store evaluation version/model metadata for comparison. |
| AI call is expensive | Filter candidates before AI evaluation and apply budgets. |

## 5. Matching

| Case | Required behavior |
|---|---|
| User has no skills | Return limited matching and explain missing profile information. |
| User has many skills | Avoid score inflation from unrelated skills. |
| Synonymous skills | Normalize common aliases before comparison. |
| Senior role for junior user | Penalize experience mismatch; do not automatically claim ineligibility unless requirement is hard. |
| Excellent skill match but impossible location | Hard location constraint should exclude when configured as required. |
| Great match with deadline tomorrow | Increase urgency separately from fit score. |
| Old but still active listing | Reduce freshness signal, not necessarily hard-exclude. |
| No opportunities match | Return an honest empty state and suggest broadening filters. |

## 6. Notifications

| Case | Required behavior |
|---|---|
| Same opportunity discovered repeatedly | Do not send repeated new-opportunity notifications. |
| User saves an opportunity | Do not send a duplicate discovery alert. |
| Notification provider fails | Retry safely; do not duplicate successful deliveries. |
| User disabled notifications | Do not send. |
| Quiet hours | Queue or defer non-urgent notifications. |
| Deadline changes | Notify only when the change is meaningful and policy allows. |
| Deadline passes during queue delay | Suppress stale alert. |
| User receives too many matches | Apply digest/throttling rules. |
| User has no verified channel | Keep notification pending/unavailable rather than failing the workflow. |

## 7. Application Tracking

| Case | Required behavior |
|---|---|
| User marks expired opportunity as applied | Allow only if historical policy permits; preserve timestamps. |
| User changes applied → saved | Permit only through an explicit state transition policy. |
| Opportunity deleted/archived after application | Preserve application history. |
| Duplicate application record | Enforce uniqueness per user/opportunity unless multiple applications are explicitly supported. |
| User enters invalid follow-up date | Validate against application and deadline context. |
| Deadline passes after application | Keep application active; opportunity expiry does not erase application history. |

## 8. Automation and Concurrency

| Case | Required behavior |
|---|---|
| Same workflow starts twice | Idempotency prevents duplicate side effects. |
| Two workers process same opportunity | Use database constraints/locks or idempotent upserts. |
| Worker crashes after persistence but before acknowledgement | Safe retry must not duplicate records. |
| Notification succeeds but worker crashes | Delivery idempotency prevents a duplicate notification. |
| Queue unavailable | API remains usable for supported synchronous operations; background work becomes degraded. |
| Job exceeds timeout | Cancel/mark timed out and retry only when safe. |
| Retry storm | Exponential backoff and maximum attempts. |
| Dead-letter job | Persist failure and expose recovery path. |

## 9. Data and Privacy

| Case | Required behavior |
|---|---|
| User requests deletion | Delete/anonymize according to retention policy and preserve only legally/operationally necessary records. |
| Logs contain profile data | Minimize or redact personal data. |
| Secrets appear in user-provided text | Do not echo or persist them unnecessarily. |
| Source contains personal data about recruiters/applicants | Store only data required for the product. |
| Database backup exposed | Encrypt and restrict access. |

## 10. Security

- Never expose LLM/provider keys to the frontend.
- Never execute code or tool commands because an opportunity description requests it.
- Validate all webhook signatures where providers support them.
- Rate-limit authenticated and public endpoints appropriately.
- Prevent SSRF when fetching URLs supplied by external sources or users.
- Restrict internal/admin endpoints.
- Validate redirects and fetched domains according to source policy.
- Do not allow arbitrary outbound requests through a generic fetch endpoint.

## 11. Operational Edge Cases

- Database temporarily unavailable.
- Migration fails halfway through deployment.
- Clock/time-zone mismatch changes deadline interpretation.
- Daylight-saving transition affects a reminder in a supported timezone.
- Source uses a date with no timezone.
- Source deadline is "rolling" or has no fixed date.
- AI provider changes model behavior without a code deployment.
- Notification provider changes API schema.
- User changes preferences after opportunities were already scored.
- User changes location or experience level.
- Opportunity is edited after a user saved it.
- Opportunity deadline is extended.
- Source marks a fraudulent or suspicious listing as active.

## 12. Priority

### P0 — Must handle before MVP

- Secret exposure prevention.
- Prompt injection from external content.
- Duplicate ingestion.
- Duplicate notifications.
- Hard eligibility vs AI disagreement.
- Source failure isolation.
- Retry storms.
- Concurrent job execution.
- Invalid AI output.
- Deadline/time-zone correctness.

### P1 — Handle during MVP hardening

- Source schema drift.
- URL changes.
- Partial source runs.
- Notification provider outages.
- User profile changes.
- Opportunity edits.
- Dead-letter recovery.
- Privacy deletion flows.

### P2 — Later

- Advanced fraud detection.
- Cross-source entity resolution beyond deterministic fingerprints.
- Personalized digest optimization.
- Advanced recommendation experimentation.

## 13. Edge-Case Design Rule

When uncertain, the system should prefer:

**preserve data + mark uncertainty + avoid irreversible action + notify the user when necessary.**

Never turn missing evidence into a confident claim.
