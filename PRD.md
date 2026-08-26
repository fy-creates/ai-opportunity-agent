# AI Opportunity Agent — Product Requirements Document

**Status:** Draft
**Branch:** `architecture`
**Version:** 0.1

## 1. Product Summary

AI Opportunity Agent discovers relevant jobs, internships, scholarships, fellowships, grants, competitions, and other career-building opportunities; evaluates them against a user's profile; removes duplicates; ranks opportunities by fit and urgency; and delivers useful notifications without overwhelming the user.

The product is an **opportunity intelligence and workflow system**, not a generic chatbot and not an automatic application bot.

## 2. Problem

Opportunity seekers face three recurring problems:

1. Opportunities are scattered across many sources.
2. Generic search results create too much noise.
3. Deadlines and application status are difficult to track consistently.

The system should reduce discovery effort while preserving user control over decisions and applications.

## 3. Target Users

### Primary
- Students and recent graduates seeking internships and entry-level roles.
- Early-career developers, designers, analysts, and other professionals.

### Secondary
- Users seeking scholarships, fellowships, grants, competitions, bootcamps, and other development opportunities.

## 4. Goals

- Build a reliable opportunity ingestion pipeline.
- Maintain a structured, deduplicated opportunity database.
- Represent a user's skills, education, preferences, eligibility, and goals.
- Produce explainable match scores rather than opaque recommendations.
- Notify users about high-value new opportunities and approaching deadlines.
- Track opportunities through states such as discovered, saved, applied, interview, rejected, accepted, and expired.
- Make automation observable, retryable, and safe.
- Keep AI optional at the infrastructure level so deterministic rules remain authoritative where appropriate.

## 5. Non-Goals for MVP

- Automatically submitting job or scholarship applications.
- Automatically sending messages to employers.
- Guaranteeing that an opportunity is legitimate.
- Guaranteeing eligibility or employment outcomes.
- Building a social network for applicants.
- Replacing the user's final judgment.

## 6. Core User Flow

```text
Create profile
    ↓
Configure opportunity preferences
    ↓
System discovers opportunities
    ↓
Normalize + validate + deduplicate
    ↓
Eligibility filtering
    ↓
AI-assisted relevance scoring
    ↓
Rank opportunities
    ↓
Notify user / show dashboard
    ↓
User saves or dismisses
    ↓
User applies externally
    ↓
Track application status + deadlines
```

## 7. MVP Scope

### 7.1 User Profile

Store:
- Name and optional public profile information.
- Skills.
- Education.
- Experience level.
- Preferred opportunity types.
- Preferred locations.
- Remote/hybrid/on-site preference.
- Work authorization/eligibility constraints where voluntarily provided.
- Target roles.
- Preferred industries.
- Minimum/target compensation when applicable.
- Availability.
- Career interests.

### 7.2 Opportunity Ingestion

Each opportunity should have normalized fields including:
- title
- organization
- opportunity type
- description
- source
- canonical URL
- location
- remote status
- compensation when available
- eligibility requirements
- required/preferred skills
- deadline
- discovered timestamp
- source timestamp when available
- freshness status

MVP sources should be limited to sources that can be accessed reliably and legally. Source adapters must be isolated from the core domain.

### 7.3 Matching

The matching pipeline should combine:

1. Hard eligibility rules.
2. Preference matching.
3. Skill overlap.
4. Role similarity.
5. Location/remote compatibility.
6. Experience compatibility.
7. Deadline urgency.
8. AI semantic relevance where useful.

The final score must be explainable through positive and negative factors.

### 7.4 Notifications

MVP notification channel:
- Telegram and/or email, selected during implementation based on integration simplicity.

Notifications should be preference-aware and deduplicated.

### 7.5 Application Tracking

Users can manually update status:
- saved
- applied
- screening
- interview
- offer
- accepted
- rejected
- withdrawn
- expired

The system can generate reminders from deadlines and user-defined follow-up dates.

## 8. Functional Requirements

### FR-1 Discovery
The system SHALL discover opportunities on a scheduled basis and record source provenance.

### FR-2 Normalization
The system SHALL normalize source-specific records into a common opportunity model.

### FR-3 Deduplication
The system SHALL prevent the same opportunity from appearing repeatedly when the same listing is discovered through multiple runs or sources.

### FR-4 Eligibility
The system SHALL distinguish hard eligibility failures from soft preference mismatches.

### FR-5 Matching
The system SHALL calculate a match score and provide an explanation of major score factors.

### FR-6 Ranking
The system SHALL rank eligible opportunities using relevance and configurable urgency signals.

### FR-7 Notifications
The system SHALL send notifications only for opportunities that satisfy configured thresholds and notification rules.

### FR-8 Tracking
The system SHALL allow users to track application state and deadlines.

### FR-9 Provenance
Every opportunity SHALL retain source, canonical URL, discovery time, and relevant source metadata.

### FR-10 Auditability
Important automated decisions SHALL be logged with enough metadata to reproduce or diagnose the decision.

### FR-11 Human Control
The system SHALL NOT submit applications or make irreversible external actions without explicit user approval.

## 9. Non-Functional Requirements

- **Reliability:** transient source/API failures must not corrupt stored opportunities.
- **Idempotency:** rerunning an ingestion workflow should not create duplicate records.
- **Observability:** jobs, failures, latency, and AI usage should be measurable.
- **Security:** secrets remain server-side and are never exposed to the browser.
- **Privacy:** user profile data must be minimized and protected.
- **Cost control:** AI calls should be selective and measurable.
- **Extensibility:** new opportunity types and sources should not require rewriting the core domain.
- **Testability:** ingestion, matching, notification, and tracking logic must be independently testable.

## 10. Success Metrics

Initial engineering metrics:
- Opportunity ingestion success rate.
- Duplicate rate.
- Percentage of opportunities with valid canonical URLs.
- Match precision measured through user feedback.
- Notification open/click rate where measurable.
- Percentage of expired opportunities detected correctly.
- Average cost per evaluated opportunity.
- Workflow failure/retry rate.

Product validation should prioritize **useful opportunities per notification** over the raw number of opportunities collected.

## 11. MVP Acceptance Criteria

The MVP is acceptable when a test user can:

1. Create a profile.
2. Configure opportunity preferences.
3. Run or schedule discovery.
4. See normalized opportunities.
5. Receive a meaningful match score with explanation.
6. Save/dismiss opportunities.
7. Track an application.
8. Receive deadline reminders.
9. Avoid duplicate notifications for the same opportunity.
10. Recover from temporary source or AI failures without losing valid data.

## 12. Roadmap

### Phase 0 — Architecture
Requirements, domain model, edge cases, agent boundaries, repository standards.

### Phase 1 — Foundation
Backend, database, configuration, source adapter interface, core models, tests.

### Phase 2 — Discovery
First reliable source adapters, normalization, deduplication, freshness handling.

### Phase 3 — Intelligence
Profile matching, explainable scoring, AI semantic evaluation, evaluation dataset.

### Phase 4 — Automation
Scheduled workflows, notifications, deadline monitoring, retries, observability.

### Phase 5 — Product
Dashboard, authentication, application tracker, user feedback loops.

### Phase 6 — Hardening
Security, rate limits, cost controls, source health monitoring, production deployment.
