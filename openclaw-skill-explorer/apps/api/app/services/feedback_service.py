from __future__ import annotations

from collections import defaultdict
import json

from sqlalchemy.orm import Session

from app.models.policy_change_log import PolicyChangeLog
from app.models.skill import Skill
from app.models.skill_audit_log import SkillAuditLog
from app.models.skill_feedback import SkillFeedback

ALLOWED_FEEDBACK_TYPES = {
    "false_positive",
    "false_negative",
    "incorrect_risk_level",
    "missing_signal",
    "noisy_signal",
    "documentation_gap",
    "other",
}
ALLOWED_FEEDBACK_STATUSES = {"open", "triaged", "planned", "resolved"}
ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}
ALLOWED_CHANGE_TYPES = {"rule_tuning", "weight_update", "keyword_update", "process_update"}
SEVERITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def create_skill_feedback(
    db: Session,
    *,
    skill: Skill,
    reporter: str,
    feedback_type: str,
    severity: str = "medium",
    status: str = "open",
    expected_risk_level: str | None = None,
    actual_risk_level: str | None = None,
    comment: str | None = None,
    risk_report_id: int | None = None,
) -> SkillFeedback:
    normalized_feedback_type = feedback_type.strip().lower()
    normalized_severity = severity.strip().lower()
    normalized_status = status.strip().lower()
    normalized_expected = expected_risk_level.strip().upper() if expected_risk_level else None
    normalized_actual = actual_risk_level.strip().upper() if actual_risk_level else None

    if normalized_feedback_type not in ALLOWED_FEEDBACK_TYPES:
        raise ValueError(f"Unsupported feedback_type: {feedback_type}")
    if normalized_severity not in ALLOWED_SEVERITIES:
        raise ValueError(f"Unsupported severity: {severity}")
    if normalized_status not in ALLOWED_FEEDBACK_STATUSES:
        raise ValueError(f"Unsupported status: {status}")

    feedback = SkillFeedback(
        skill_id=skill.id,
        risk_report_id=risk_report_id,
        reporter=(reporter or "system").strip() or "system",
        feedback_type=normalized_feedback_type,
        severity=normalized_severity,
        status=normalized_status,
        expected_risk_level=normalized_expected,
        actual_risk_level=normalized_actual,
        comment=(comment or "").strip() or None,
    )
    db.add(feedback)
    db.flush()

    db.add(
        SkillAuditLog(
            skill_id=skill.id,
            action_type="feedback_created",
            actor=feedback.reporter,
            payload_json=json.dumps(
                {
                    "feedback_id": feedback.id,
                    "feedback_type": feedback.feedback_type,
                    "severity": feedback.severity,
                    "status": feedback.status,
                },
                ensure_ascii=True,
            ),
        )
    )
    db.flush()
    return feedback


def list_skill_feedback(db: Session, skill_id: int) -> list[SkillFeedback]:
    return (
        db.query(SkillFeedback)
        .filter(SkillFeedback.skill_id == skill_id)
        .order_by(SkillFeedback.created_at.desc(), SkillFeedback.id.desc())
        .all()
    )


def summarize_feedback(db: Session, status: str | None = None) -> dict:
    query = db.query(SkillFeedback)
    if status:
        query = query.filter(SkillFeedback.status == status.strip().lower())

    rows = query.order_by(SkillFeedback.created_at.desc(), SkillFeedback.id.desc()).all()

    by_type: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    backlog_scores: dict[str, dict] = {}
    for item in rows:
        by_type[item.feedback_type] += 1
        by_severity[item.severity] += 1
        backlog_entry = backlog_scores.setdefault(
            item.feedback_type,
            {
                "feedback_type": item.feedback_type,
                "count": 0,
                "severity_score": 0,
                "priority_score": 0,
            },
        )
        backlog_entry["count"] += 1
        backlog_entry["severity_score"] += SEVERITY_WEIGHTS.get(item.severity, 1)
        backlog_entry["priority_score"] = backlog_entry["count"] * backlog_entry["severity_score"]

    prioritized_items = sorted(
        backlog_scores.values(),
        key=lambda item: (-item["priority_score"], -item["count"], item["feedback_type"]),
    )

    recent_items = rows[:20]
    return {
        "total_feedback": len(rows),
        "by_type": dict(sorted(by_type.items())),
        "by_severity": dict(sorted(by_severity.items())),
        "prioritized_items": prioritized_items,
        "recent_items": recent_items,
    }


def create_policy_change_log(
    db: Session,
    *,
    policy_version: str,
    title: str,
    change_type: str,
    summary: str,
    author: str,
    related_feedback_count: int = 0,
) -> PolicyChangeLog:
    normalized_change_type = change_type.strip().lower()
    if normalized_change_type not in ALLOWED_CHANGE_TYPES:
        raise ValueError(f"Unsupported change_type: {change_type}")

    entry = PolicyChangeLog(
        policy_version=policy_version.strip(),
        title=title.strip(),
        change_type=normalized_change_type,
        summary=summary.strip(),
        author=(author or "system").strip() or "system",
        related_feedback_count=max(0, int(related_feedback_count)),
    )
    db.add(entry)
    db.flush()
    return entry


def list_policy_change_logs(db: Session, limit: int = 50) -> list[PolicyChangeLog]:
    return (
        db.query(PolicyChangeLog)
        .order_by(PolicyChangeLog.published_at.desc(), PolicyChangeLog.id.desc())
        .limit(limit)
        .all()
    )
