from __future__ import annotations

import json
from datetime import datetime
from typing import TypedDict

from sqlalchemy.orm import Session

from app.models.skill import Skill
from app.models.skill_audit_log import SkillAuditLog
from app.models.skill_review import SkillReview

ALLOWED_DECISIONS = {"approved", "blocked", "needs_remediation", "pending_review"}
DEFAULT_REVIEW_STATE = "pending_review"


class RemediationChecklistItem(TypedDict):
    capability: str
    priority: int
    title: str
    guidance: str


REMEDIATION_TEMPLATES: dict[str, RemediationChecklistItem] = {
    "secrets_access": {
        "capability": "secrets_access",
        "priority": 1,
        "title": "Restrict secret access scope",
        "guidance": "Provide only required secrets and rotate credentials after validation tests.",
    },
    "shell_exec": {
        "capability": "shell_exec",
        "priority": 2,
        "title": "Constrain shell execution",
        "guidance": "Limit command allow-lists and run in isolated execution environments.",
    },
    "external_download": {
        "capability": "external_download",
        "priority": 3,
        "title": "Pin and verify downloads",
        "guidance": "Allow only trusted artifact sources and verify checksums before execution.",
    },
    "network_access": {
        "capability": "network_access",
        "priority": 4,
        "title": "Narrow outbound network scope",
        "guidance": "Restrict egress destinations and enforce domain/IP allow-lists.",
    },
    "file_write": {
        "capability": "file_write",
        "priority": 5,
        "title": "Reduce write permissions",
        "guidance": "Use least-privilege filesystem paths and protect sensitive directories.",
    },
    "app_access": {
        "capability": "app_access",
        "priority": 6,
        "title": "Minimize app connector scopes",
        "guidance": "Grant the smallest set of app permissions required for business tasks.",
    },
    "file_read": {
        "capability": "file_read",
        "priority": 7,
        "title": "Limit file read boundaries",
        "guidance": "Allow access only to approved workspace paths and avoid system directories.",
    },
    "unclear_docs": {
        "capability": "unclear_docs",
        "priority": 8,
        "title": "Improve documentation quality",
        "guidance": "Require explicit behavior, permission, and data-flow documentation before approval.",
    },
}


def create_skill_review(
    db: Session,
    *,
    skill: Skill,
    reviewer: str,
    decision: str,
    comment: str | None = None,
    override_reason: str | None = None,
) -> SkillReview:
    normalized_decision = decision.strip().lower()
    if normalized_decision not in ALLOWED_DECISIONS:
        raise ValueError(f"Unsupported decision: {decision}")

    review = SkillReview(
        skill_id=skill.id,
        reviewer=(reviewer or "system").strip() or "system",
        decision=normalized_decision,
        comment=(comment or "").strip() or None,
        override_reason=(override_reason or "").strip() or None,
    )
    db.add(review)
    db.flush()

    # Immutable audit entry: decision actions are append-only.
    audit_entry = SkillAuditLog(
        skill_id=skill.id,
        action_type="review_decision_created",
        actor=review.reviewer,
        payload_json=json.dumps(
            {
                "review_id": review.id,
                "decision": review.decision,
                "comment": review.comment,
                "override_reason": review.override_reason,
                "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            },
            ensure_ascii=True,
        ),
    )
    db.add(audit_entry)
    db.flush()
    return review


def list_skill_reviews(db: Session, skill_id: int) -> list[SkillReview]:
    return (
        db.query(SkillReview)
        .filter(SkillReview.skill_id == skill_id)
        .order_by(SkillReview.created_at.desc(), SkillReview.id.desc())
        .all()
    )


def get_skill_review_state(skill: Skill) -> str:
    if not skill.reviews:
        return DEFAULT_REVIEW_STATE
    latest_review = max(skill.reviews, key=lambda item: (item.created_at, item.id))
    return latest_review.decision or DEFAULT_REVIEW_STATE


def get_latest_skill_review(skill: Skill) -> SkillReview | None:
    if not skill.reviews:
        return None
    return max(skill.reviews, key=lambda item: (item.created_at, item.id))


def build_remediation_checklist(flags: dict[str, bool]) -> list[RemediationChecklistItem]:
    items: list[RemediationChecklistItem] = []
    for capability, enabled in flags.items():
        if enabled and capability in REMEDIATION_TEMPLATES:
            items.append(REMEDIATION_TEMPLATES[capability])
    items.sort(key=lambda item: item["priority"])
    return items


def list_skill_audit_logs(db: Session, skill_id: int) -> list[SkillAuditLog]:
    return (
        db.query(SkillAuditLog)
        .filter(SkillAuditLog.skill_id == skill_id)
        .order_by(SkillAuditLog.created_at.desc(), SkillAuditLog.id.desc())
        .all()
    )
