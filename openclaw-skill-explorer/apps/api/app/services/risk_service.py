from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.risk_report import RiskReport
from app.models.skill import Skill
from app.services.recommendation_enhancer import enhance_recommendations
from app.services.risk_engine import scan_text
from app.services.risk_explainer import refine_risk_explanation
from app.services.text_utils import build_skill_analysis_text

CAPABILITY_FIELDS = [
    "file_read",
    "file_write",
    "network_access",
    "shell_exec",
    "secrets_access",
    "external_download",
    "app_access",
    "unclear_docs",
]


def _to_int_flag(value: bool) -> int:
    return 1 if value else 0


def _safe_json_loads(raw: str | None, fallback):
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def _build_permissions_detected(flags: dict[str, bool]) -> list[str]:
    return [field for field in CAPABILITY_FIELDS if flags.get(field)]


def _build_sensitive_scopes(flags: dict[str, bool]) -> list[str]:
    scopes = []
    if flags.get("secrets_access"):
        scopes.append("secrets")
    if flags.get("app_access"):
        scopes.append("connected_apps")
    if flags.get("network_access"):
        scopes.append("network")
    return scopes


def create_risk_report_for_skill(db: Session, skill: Skill) -> tuple[RiskReport, dict]:
    analysis_text = build_skill_analysis_text(skill)
    scan_result = scan_text(
        analysis_text,
        metadata_context={
            "description": skill.description,
            "readme": skill.raw_readme,
        },
    )
    report = _persist_risk_report(
        db=db,
        skill_id=skill.id,
        input_type="skill",
        scan_result=scan_result,
    )
    return report, scan_result


def create_risk_report_from_text(db: Session, input_type: str, text: str) -> tuple[RiskReport, dict]:
    scan_result = scan_text(
        text,
        metadata_context={
            "description": None,
            "readme": text if input_type == "readme" else None,
        },
    )
    report = _persist_risk_report(
        db=db,
        skill_id=None,
        input_type=input_type,
        scan_result=scan_result,
    )
    return report, scan_result


def _persist_risk_report(
    db: Session,
    skill_id: int | None,
    input_type: str,
    scan_result: dict,
) -> RiskReport:
    flags = scan_result["flags"]
    reasons = scan_result["reasons"]
    matched_keywords = scan_result.get("matched_keywords", {})
    evidence_snippets = scan_result.get("evidence_snippets", [])
    policy_version = scan_result.get("policy_version", "v1.0.0")
    base_explanation = " ".join(reasons).strip()
    explanation = refine_risk_explanation(
        flags=flags,
        matched_keywords=matched_keywords,
        base_reasons=reasons,
    )
    if not explanation:
        explanation = base_explanation

    recommendations = enhance_recommendations(
        risk_level=scan_result["risk_level"],
        flags=flags,
        base_recommendations=scan_result["recommendations"],
    )

    report = RiskReport(
        skill_id=skill_id,
        input_type=input_type,
        risk_level=scan_result["risk_level"],
        risk_score=scan_result["risk_score"],
        file_read=_to_int_flag(flags.get("file_read", False)),
        file_write=_to_int_flag(flags.get("file_write", False)),
        network_access=_to_int_flag(flags.get("network_access", False)),
        shell_exec=_to_int_flag(flags.get("shell_exec", False)),
        secrets_access=_to_int_flag(flags.get("secrets_access", False)),
        external_download=_to_int_flag(flags.get("external_download", False)),
        app_access=_to_int_flag(flags.get("app_access", False)),
        unclear_docs=_to_int_flag(flags.get("unclear_docs", False)),
        permissions_detected=json.dumps(_build_permissions_detected(flags)),
        sensitive_scopes=json.dumps(_build_sensitive_scopes(flags)),
        findings_json=json.dumps(
            {
                "policy_version": policy_version,
                "matched_keywords": matched_keywords,
                "evidence_snippets": evidence_snippets,
                "reasons": reasons,
            }
        ),
        explanation=explanation,
        recommendations=json.dumps(recommendations),
        scanned_at=datetime.utcnow(),
    )
    db.add(report)
    db.flush()
    return report


def get_latest_risk_report_for_skill(db: Session, skill_id: int) -> RiskReport | None:
    return (
        db.query(RiskReport)
        .filter(RiskReport.skill_id == skill_id)
        .order_by(RiskReport.scanned_at.desc(), RiskReport.id.desc())
        .first()
    )


def list_recent_risk_reports_for_skill(db: Session, skill_id: int, limit: int = 2) -> list[RiskReport]:
    return (
        db.query(RiskReport)
        .filter(RiskReport.skill_id == skill_id)
        .order_by(RiskReport.scanned_at.desc(), RiskReport.id.desc())
        .limit(limit)
        .all()
    )


def compute_scan_delta(previous_report: RiskReport, current_report: RiskReport) -> dict:
    previous = risk_report_to_scan_result(previous_report)
    current = risk_report_to_scan_result(current_report)

    previous_flags = {name for name, enabled in previous["flags"].items() if enabled}
    current_flags = {name for name, enabled in current["flags"].items() if enabled}

    added_flags = sorted(list(current_flags - previous_flags))
    removed_flags = sorted(list(previous_flags - current_flags))
    persisted_flags = sorted(list(previous_flags.intersection(current_flags)))

    return {
        "previous_report_id": previous_report.id,
        "current_report_id": current_report.id,
        "previous_scanned_at": previous_report.scanned_at,
        "current_scanned_at": current_report.scanned_at,
        "previous_policy_version": previous.get("policy_version", "v1.0.0"),
        "current_policy_version": current.get("policy_version", "v1.0.0"),
        "previous_risk_level": previous["risk_level"],
        "current_risk_level": current["risk_level"],
        "previous_risk_score": previous["risk_score"],
        "current_risk_score": current["risk_score"],
        "score_delta": current["risk_score"] - previous["risk_score"],
        "added_flags": added_flags,
        "removed_flags": removed_flags,
        "persisted_flags": persisted_flags,
    }


def risk_report_to_scan_result(report: RiskReport) -> dict:
    findings = _safe_json_loads(report.findings_json, {})
    policy_version = findings.get("policy_version", "v1.0.0")
    matched_keywords = findings.get("matched_keywords", {})
    evidence_snippets = findings.get("evidence_snippets", [])
    reasons = findings.get("reasons", [])
    recommendations = _safe_json_loads(report.recommendations, [])

    flags = {
        "file_read": bool(report.file_read),
        "file_write": bool(report.file_write),
        "network_access": bool(report.network_access),
        "shell_exec": bool(report.shell_exec),
        "secrets_access": bool(report.secrets_access),
        "external_download": bool(report.external_download),
        "app_access": bool(report.app_access),
        "unclear_docs": bool(report.unclear_docs),
    }

    return {
        "policy_version": policy_version,
        "risk_level": report.risk_level,
        "risk_score": report.risk_score,
        "explanation": report.explanation or "",
        "flags": flags,
        "matched_keywords": matched_keywords,
        "evidence_snippets": evidence_snippets,
        "reasons": reasons,
        "recommendations": recommendations,
    }
