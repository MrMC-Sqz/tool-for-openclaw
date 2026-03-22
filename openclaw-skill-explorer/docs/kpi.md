# KPI and Release Gates

## Objective
Move from demo usability to measurable production value for security/platform reviewers.

## KPI Set

### 1) Decision Efficiency
- Median review time per skill (target): <= 8 minutes.
- P90 review time per skill (target): <= 15 minutes.

### 2) Decision Quality (Proxy)
- False-positive review rate (target): <= 20% after calibration period.
- High-risk catch rate on labeled set (target): >= 85%.

### 3) Workflow Completion
- Review completion rate (opened review -> final decision) (target): >= 90%.
- Remediation closure rate within 7 days (target): >= 60%.

### 4) Adoption
- Weekly active reviewers (target): >= 5 for pilot team.
- Weekly reviewed skills (target): >= 30 in pilot phase.

## Phase Gates

### Gate A - Data Reliability
Must pass before policy workflow expansion:
- Successful sync run rate >= 95% over trailing 7 days.
- Duplicate skill rate <= 2%.
- Broken source record rate <= 5%.

### Gate B - Risk Explainability
Must pass before scaling reviewer access:
- 100% of reports include flags + reasons + recommendations.
- Policy/rule version persisted for all new reports.
- Evidence snippet available for top matched risks.

### Gate C - Workflow Readiness
Must pass before broad rollout:
- Explicit decision state lifecycle in product.
- Audit trail for decision changes.
- Re-scan delta view for remediation validation.

## Measurement Notes
- Use immutable event logging for review actions.
- Measure KPIs weekly; review trends bi-weekly.
- Do not change thresholds during a release cycle unless blocked by data quality issues.
