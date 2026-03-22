# OpenClaw Skill Explorer + Risk Scanner Task List

## Phase 1 - Real User Problem Definition (Current)

### P1.1 Target User and Core Job-to-be-Done
- [x] Define primary user: security/platform reviewer evaluating third-party skills before enablement.
- [x] Define primary workflow: discover -> assess risk -> decide allow/block -> track remediation.
- [x] Define out-of-scope workflows for MVP productionization.

### P1.2 Success Metrics
- [x] Define decision quality metrics (precision/recall proxy, false-positive review rate).
- [x] Define efficiency metrics (median review time, time-to-decision).
- [x] Define adoption metrics (weekly reviews, approval rate after remediation).

### P1.3 Acceptance Baseline
- [x] Convert goals into measurable release gates.
- [x] Create two-week execution plan ordered by impact and risk.

## Phase 2 - Data Pipeline Beyond Demo Seed

### P2.1 Source Expansion
- [x] Add pluggable source config (multiple source files/endpoints).
- [x] Add source health reporting and last-sync visibility.
- [x] Add deduplication guards across repo_url + slug + normalized names.

### P2.2 Ingestion Reliability
- [x] Add structured sync logs and error categorization.
- [x] Add retry strategy for transient source/API failures.
- [x] Add idempotent incremental sync behavior.

## Phase 3 - Risk Governance (Deterministic Core)

### P3.1 Policy Versioning
- [x] Version risk rules and score weights.
- [x] Persist rule_version with every risk report.
- [x] Add comparison helpers between policy versions.

### P3.2 Explainability and Auditability
- [x] Persist evidence snippets for each matched rule.
- [x] Add review comments / override reasons (manual workflow).
- [x] Add immutable audit log for decision actions.

## Phase 4 - User Workflow Closure

### P4.1 Decision Workflow
- [x] Add explicit states: pending_review, approved, blocked, needs_remediation.
- [x] Add remediation checklist templates by capability class.
- [x] Add re-scan comparison view (before/after risk deltas).

### P4.2 Team Collaboration
- [x] Add reviewer attribution and timestamps.
- [x] Add filtering by review state and owner.
- [x] Add exportable review summary for governance reporting.

## Phase 5 - Production Engineering

### P5.1 Platform Readiness
- [x] Migrate persistence from SQLite to Postgres.
- [x] Add background jobs for ingestion and scan workloads.
- [x] Add caching for high-traffic list/detail endpoints.

### P5.2 Security and Ops
- [x] Add authentication and role-based access control.
- [x] Add structured observability (metrics, traces, error reporting).
- [x] Add backup/restore and disaster recovery runbook.

## Phase 6 - Continuous Quality

### P6.1 Risk Quality Benchmarking
- [x] Build labeled evaluation dataset.
- [x] Track false positive/false negative trends per release.
- [x] Add regression tests for risk rules.

### P6.2 Product Feedback Loop
- [x] Capture user feedback on incorrect risk outcomes.
- [x] Prioritize weekly rule-tuning updates.
- [x] Publish changelog for policy updates.
