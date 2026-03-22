# Feedback Loop

## Goal

Phase 6.2 adds a practical way to capture incorrect risk outcomes and turn them into rule-tuning priorities.

## Feedback Capture

Use skill-scoped feedback endpoints:

```bash
POST /api/skills/{slug}/feedback
GET /api/skills/{slug}/feedback
```

Recommended feedback types:

- `false_positive`
- `false_negative`
- `incorrect_risk_level`
- `missing_signal`
- `noisy_signal`
- `documentation_gap`
- `other`

## Weekly Tuning Backlog

Use the summary endpoint to see which categories should be tuned first:

```bash
GET /api/skills/feedback/summary
```

The summary ranks backlog items by:

- feedback volume
- severity mix
- combined priority score

## Feedback Export

Export recent feedback for offline triage:

```bash
GET /api/skills/feedback/export
```

## Policy Changelog

Track published rule and policy updates:

```bash
GET /api/skills/policy-changelog
POST /api/skills/policy-changelog
```

Use changelog entries to document:

- keyword updates
- score/weight changes
- reviewer workflow changes
- follow-up fixes driven by user feedback
