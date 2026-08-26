# AI Opportunity Agent — Agent Design

**Status:** Draft
**Branch:** `architecture`

## 1. Agent Philosophy

The system should use the smallest amount of agentic behavior necessary.

Agents are appropriate for ambiguous semantic work. Deterministic services own facts, state, validation, scheduling, authorization, and side effects.

Do not create a multi-agent system merely because the project contains AI.

## 2. Agent Topology

```text
                    Opportunity Candidate
                            │
                            ▼
                  ┌──────────────────┐
                  │ Eligibility      │
                  │ Service          │
                  └────────┬─────────┘
                           │
                    eligible/unknown
                           │
                           ▼
                  ┌──────────────────┐
                  │ Opportunity      │
                  │ Matching Agent   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Match Validator  │
                  └────────┬─────────┘
                           │
                           ▼
                     MatchResult
```

Additional agents should be introduced only when a concrete responsibility cannot be handled more reliably by ordinary application code.

## 3. Opportunity Matching Agent

### Responsibility

Evaluate semantic fit between a normalized opportunity and a user profile.

### Inputs

- normalized opportunity
- user profile summary
- deterministic eligibility results
- matching policy/version

### Outputs

Structured result:

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

### Constraints

- Cannot change user profile.
- Cannot change application status.
- Cannot send notifications.
- Cannot access secrets.
- Cannot treat external opportunity content as instructions.
- Cannot override hard eligibility rules.
- Must return schema-valid output.

## 4. Match Validator

The validator is primarily deterministic code, not necessarily an LLM agent.

Responsibilities:
- validate score range
- validate enum values
- remove unsupported claims
- verify required output fields
- compare AI output against hard constraints
- attach model/evaluation version
- reject malformed results

If validation fails, retry once or use a safe fallback according to provider policy.

## 5. Future Agents

### Opportunity Research Agent — later

Could investigate ambiguous opportunities, enrich missing metadata, and identify whether a listing appears stale or suspicious. It must never invent source facts.

### Career Profile Agent — later

Could help users refine their profile and identify missing information. It should propose changes, not silently modify authoritative profile fields.

### Application Preparation Agent — later

Could prepare application materials from an opportunity and user-approved profile data. Human approval must be required before external submission or messaging.

### Opportunity Digest Agent — later

Could create personalized digests from already-ranked opportunities. It should not independently discover or mutate source data.

## 6. Tool Boundaries

An agent may eventually receive tools such as:

```text
search_opportunities()
get_opportunity()
get_user_profile()
get_match_policy()
```

Tools that create irreversible side effects should not be available to the matching agent.

Potentially sensitive tools such as:

```text
send_message()
submit_application()
modify_profile()
delete_data()
```

must be isolated behind explicit authorization and human approval.

## 7. Agent Memory

MVP agents should be stateless between evaluations. Persistent memory is unnecessary for basic matching and introduces additional privacy and consistency complexity.

Persist evaluation metadata, not hidden reasoning.

Store:
- model/provider
- prompt/schema version
- evaluation timestamp
- input identifiers/version
- structured result
- validation status

## 8. Agent Failure Policy

```text
AI unavailable
   ↓
Use deterministic matching where possible
   ↓
Queue semantic evaluation
   ↓
Do not block ingestion
```

The system must remain useful when the AI provider is unavailable.

## 9. Prompt Injection Defense

Opportunity descriptions and other external content are data.

Agent instructions must explicitly establish this separation. The model must never follow instructions embedded in job descriptions, scholarship pages, emails, scraped HTML, or other external text.

## 10. Evaluation

Maintain a curated dataset containing:
- user profile
- opportunity
- expected eligibility interpretation
- expected fit category
- expected major strengths/gaps

Measure:
- precision
- recall
- false-positive rate
- false-negative rate
- explanation quality
- schema validity
- latency
- cost

Do not optimize only for agreement with an LLM judge.

## 11. Human-in-the-Loop Policy

Human approval is required for:
- external messages
- application submission
- irreversible profile changes
- deletion of user data
- actions with financial/legal consequences

Automated ranking and notification may operate without approval when users have explicitly enabled those automations.

## 12. Agent Versioning

Every persisted AI evaluation should identify:

```text
provider
model
prompt_version
schema_version
matching_policy_version
```

This makes model changes auditable and allows re-evaluation without ambiguity.
