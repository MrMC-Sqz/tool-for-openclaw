# User Problem Definition

## Primary User
- Security reviewer / platform engineer responsible for approving third-party skills before internal enablement.

## Core Job-to-be-Done
- "Before enabling a skill, I need to quickly understand what it does, what it can access, and whether it is safe enough for my environment."

## Current Pain Points
- Skill metadata is fragmented and inconsistent.
- Risk signals are buried in README/manifests and hard to compare.
- Approval decisions are often manual, non-repeatable, and weakly documented.

## Required Outcome
- A reviewer can make a defendable allow/block decision in minutes with clear evidence and recommended remediation.

## In-Scope Workflow (Production Track)
1. Discover candidate skill.
2. Review summary + capabilities + risk score + reasons.
3. Decide `approve` / `block` / `needs_remediation`.
4. If remediation required, re-scan and compare delta.
5. Record final decision with traceable rationale.

## Out of Scope (for current track)
- Runtime sandbox execution of skill code.
- Organization-wide policy engine integration (external IAM/PAM).
- Automatic deployment of approved skills.

## Non-Functional Expectations
- Deterministic core risk output.
- Explainable scoring with evidence.
- Reliable operation under routine team usage.
